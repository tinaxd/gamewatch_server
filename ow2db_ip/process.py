# import os

import io

import cv2
import numpy as np
import scipy.signal
from PIL import Image

from ow2db_web.models import OW2UserImage


def make_1d(img_filename) -> tuple[list[bytes], list[np.ndarray]]:
    image = cv2.imread(img_filename, 0)  # 0 for grayscale
    image = cv2.resize(image, (1920, 1080))

    hists = []
    left = (270 + 170 + 10, 270 + 135)
    right = (700 - 20, 680 + left[1] - left[0])
    entry_height = 50
    topbottom = [
        200,
        260,
        330,
        390,
        450,
        620,
        680,
        740,
        800,
        865,
    ]

    threshes = []

    for i, tb in enumerate(topbottom):
        if i < 5:
            le = left[0]
            r = right[0]
        else:
            le = left[1]
            r = right[1]
        cut_img = image[tb : tb + entry_height, le:r]

        _, thresh = cv2.threshold(cut_img, 150, 255, cv2.THRESH_BINARY)
        thresh_bin = Image.fromarray(thresh)
        thresh_bytes = io.BytesIO()
        thresh_bin.save(thresh_bytes, format="PNG")
        threshes.append(thresh_bytes.getvalue())

        x1, y1 = 10.59, 28.55
        x2, y2 = 14.50, 11.40
        katamuki = (y2 - y1) / (x2 - x1)
        rot_rad = np.pi / 2 + np.arctan(katamuki)

        # extend thresh by 100 px
        pad_size = 30
        thresh_pad = np.pad(
            thresh, ((0, pad_size), (0, 0)), "constant", constant_values=0
        )

        rot_thresh = cv2.warpAffine(
            thresh_pad,
            cv2.getRotationMatrix2D(
                (thresh_pad.shape[1] / 2, thresh_pad.shape[0] / 2),
                rot_rad * 180 / np.pi,
                1.0,
            ),
            (thresh_pad.shape[1], thresh_pad.shape[0]),
        )

        # カーネルを作成する。
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
        # 2値画像を収縮する。
        erode_rot_thresh = cv2.erode(rot_thresh, kernel)

        # integrate image along the y-axis
        integrated = np.sum(erode_rot_thresh, axis=0)
        # normalize it
        integrated = integrated / np.max(integrated)

        # segments = split_array_segments(integrated, 0.05)
        # for seg in segments:
        #     plt.axvspan(seg[0], seg[1], alpha=0.5, color='red')
        # plt.imshow(rot_thresh, cmap='gray')
        # plt.show()

        hists.append(integrated)

    return threshes, hists


# calculate correlation all_hists[k] vs all others
def find_same_user(user_img_id) -> int | None:
    assigned_user_img_ids = (
        OW2UserImage.objects.filter(ow2_user__isnull=False)
        .filter(histogram__isnull=False)
        .only("id", "ow2_user_id")
        .all()
    )
    my_hist = np.load(
        io.BytesIO(OW2UserImage.objects.get(id=user_img_id).histogram.read())
    )

    corrs = []
    for assigned_user_img_id in assigned_user_img_ids:
        user_img = OW2UserImage.objects.get(id=assigned_user_img_id.id)
        user_img_hist = np.load(io.BytesIO(user_img.histogram.read()))
        r_xy = scipy.signal.correlate(my_hist, user_img_hist, mode="same")
        r_xx = np.sum(np.power(my_hist, 2))
        r_yy = np.sum(np.power(user_img_hist, 2))

        if r_xx.all() == 0 or r_yy.all() == 0:
            corrs.append(r_xy * 0)
            continue

        corrs.append(r_xy / np.sqrt(r_xx * r_yy))

    # find max correlation
    if len(corrs) == 0:
        return None
    elif len(corrs) == 1:
        max_corr = np.max(corrs)
    else:
        max_corr = np.max(corrs, axis=1)

    # find indices which are >0.95
    indices = np.where(max_corr > 0.95)[0]

    if len(indices) == 0:
        return None

    # find the user with the highest correlation
    max_user_img_id = assigned_user_img_ids[int(indices[np.argmax(max_corr[indices])])]
    return max_user_img_id.ow2_user.id
