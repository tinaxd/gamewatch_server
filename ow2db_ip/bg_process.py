import io
import logging
import tempfile
import uuid

import numpy as np
from django.core.files.base import ContentFile

from gamewatch.background import app
from ow2db_web.models import OW2UniqueUser, OW2UserImage, Screenshot

from .process import find_same_user, make_1d


@app.task
def process_screenshot_by_id(sc_id: int) -> None:
    # get screenshot image
    try:
        sc = Screenshot.objects.get(id=sc_id)
        image = sc.image

        with tempfile.NamedTemporaryFile() as tmp:
            tmp.write(image.read())
            image_name = tmp.name
            user_imgs, histos = make_1d(image_name)
        for user_img, histo in zip(user_imgs, histos):
            histo_bin = io.BytesIO()
            np.save(histo_bin, histo)
            ow2_user_img = OW2UserImage(
                original_sc=sc,
                image=ContentFile(user_img, name=uuid.uuid4().hex + ".png"),
                histogram=ContentFile(
                    histo_bin.getvalue(), name=uuid.uuid4().hex + ".npy"
                ),
            )
            ow2_user_img.save()

            inferred_unique_user = find_same_user(ow2_user_img.id)
            if inferred_unique_user is None:
                # create new UniqueUser
                unique_user = OW2UniqueUser(first_seen=sc.created_at)
                ow2_user_img.ow2_user = unique_user
                unique_user.save()
                ow2_user_img.save()
            else:
                unique_user = OW2UniqueUser.objects.get(id=inferred_unique_user)
                unique_user.last_seen = sc.created_at
                unique_user.save()
                ow2_user_img.ow2_user = unique_user
                ow2_user_img.save()

    except Screenshot.DoesNotExist:
        logging.error(f"Screenshot with id {sc_id} does not exist")
        return
