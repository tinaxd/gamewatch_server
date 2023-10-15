let canvas;
let chart;
let monthlyRecords;
let monthSelector;
let targetYearMonth = [
  // default is current
  new Date().getFullYear(),
  new Date().getMonth() + 1,
];

function updateChart() {
  const games = extractGamesFromData(monthlyRecords);
  const players = extractPlayersFromData(monthlyRecords);
  const dataset = prepareDataset(monthlyRecords, games, players);
  drawPlayTimeChart(dataset);
}

window.addEventListener("load", () => {
  monthSelector = document.getElementById("monthSelector");
  monthSelector.addEventListener("change", (event) => {
    // format in YYYY-MM
    const yearMonth = event.target.value.split("-");
    targetYearMonth = [parseInt(yearMonth[0]), parseInt(yearMonth[1])];
    updateChart();
  });

  monthlyRecords = JSON.parse(
    document.getElementById("monthly_records").textContent
  );
  canvas = document.getElementById("monthChart");
  // const labels = generateLabelsForChart(monthlyRecords);
  updateChart();
});

function generateLabelsForChart(data) {
  let years = new Set();
  let months = new Set();
  for (let i = 0; i < data.length; i++) {
    years.add(data[i].year);
    months.add(data[i].month);
  }

  const earliestYear = Math.min(...years);
  const latestYear = Math.max(...years);
  const earliestMonth = Math.min(...months);
  const latestMonth = Math.max(...months);

  let yearMonthPairs = [];
  for (let year = earliestYear; year <= latestYear; year++) {
    let startMonth = year == earliestYear ? earliestMonth : 1;
    let endMonth = year == latestYear ? latestMonth : 12;
    for (let month = startMonth; month <= endMonth; month++) {
      yearMonthPairs.push([year, month]);
    }
  }

  // latest 3 months only
  return yearMonthPairs.slice(-3);
}

function extractGamesFromData(data) {
  const games = new Set();
  for (let i = 0; i < data.length; i++) {
    const game = data[i].game;
    games.add(game);
  }
  // as list
  return [...games];
}

function extractPlayersFromData(data) {
  const players = new Set();
  for (let i = 0; i < data.length; i++) {
    const player = data[i].player;
    players.add(player);
  }
  // as list
  return [...players];
}

function yearMonthToLabelString(yearMonth) {
  const year = yearMonth[0];
  const month = yearMonth[1];
  return `${year}/${month}`;
}

function prepareDataset(data, games, players) {
  const datasets = [];

  const gameColors = [];
  // generate random colors for each game
  for (let i = 0; i < games.length; i++) {
    gameColors.push(randomColor());
  }

  for (let game of games) {
    const values = [];
    for (let player of players) {
      const year = targetYearMonth[0];
      const month = targetYearMonth[1];
      const record = data.find(
        (r) =>
          r.game == game &&
          r.player == player &&
          r.year == year &&
          r.month == month
      );
      if (record) {
        values.push(record.duration / 60);
      } else {
        values.push(0);
      }
    }
    datasets.push({
      label: game,
      data: values,
      backgroundColor: gameColors.pop(),
    });
  }

  return {
    labels: players,
    datasets: datasets,
  };
}

function drawPlayTimeChart(dataset) {
  if (chart) {
    chart.destroy();
    chart = null;
  }

  const ctx = canvas.getContext("2d");
  const config = {
    type: "bar",
    data: dataset,
    options: {
      plugins: {
        title: {
          display: true,
          text: `${yearMonthToLabelString(targetYearMonth)}`,
        },
      },
      responsive: true,
      scales: {
        x: {
          stacked: true,
        },
        y: {
          stacked: true,
          beginAtZero: true,
        },
      },
    },
  };
  chart = new Chart(ctx, config);
}
