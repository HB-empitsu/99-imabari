function checkTime() {
  // 現在の時間を取得
  const now = new Date();
  const currentHour = now.getHours();
  const currentMinute = now.getMinutes();

  const elements = document.querySelectorAll(".hide");

  if (currentHour < 17 || (currentHour === 17 && currentMinute <= 30)) {
    elements.forEach((element) => {
      element.style.display = "block";
    });
  } else {
    elements.forEach((element) => {
      element.style.display = "none";
    });
  }
}

// ページが読み込まれたときに1回実行
checkTime();

// 1分ごとに再実行
// setInterval(checkTime, 60000);
