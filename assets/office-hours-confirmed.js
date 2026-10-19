/* The receipt is stored only in this browser tab after a successful booking. */
(function () {
  "use strict";
  const root = document.getElementById("confirmation-details");
  if (!root) return;
  const zh = root.dataset.lang === "zh";
  let details;
  try {
    details = JSON.parse(sessionStorage.getItem("office-hours-confirmed-booking"));
  } catch (_) { return; }
  if (!details || !/^\d{4}-\d{2}-\d{2}$/.test(details.date) ||
      !/^\d{2}:\d{2}$/.test(details.time) || !/^\d{2}:\d{2}$/.test(details.end)) return;

  const start = new Date(details.date + "T" + details.time + ":00+08:00");
  const end = new Date(details.date + "T" + details.end + ":00+08:00");
  if (!Number.isFinite(start.getTime()) || end.getTime() - start.getTime() !== 15 * 60 * 1000) return;

  const date = new Intl.DateTimeFormat(zh ? "zh-CN" : "en-GB", {
    weekday: "long", year: "numeric", month: "long", day: "numeric", timeZone: "Asia/Shanghai"
  }).format(start);
  const heading = document.getElementById("confirmation-title");
  heading.textContent = zh ? "预约成功" : "Booking confirmed";
  document.getElementById("confirmation-when").textContent =
    date + ", " + details.time + "–" + details.end + (zh ? "（北京时间）" : " (Beijing time)");
  document.getElementById("confirmation-location").textContent =
    (zh && details.location_zh) || details.location || "Guanghua Building 2, Office 343";
  document.getElementById("confirmation-missing").hidden = true;
  root.hidden = false;
  heading.focus();

  function icsTime(value) {
    return value.toISOString().replace(/[-:]/g, "").replace(/\.\d{3}Z$/, "Z");
  }

  function icsText(value) {
    return String(value).replace(/\\/g, "\\\\").replace(/\r?\n/g, "\\n")
      .replace(/;/g, "\\;").replace(/,/g, "\\,");
  }

  document.getElementById("calendar-download").addEventListener("click", function () {
    const lines = [
      "BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Lukas Hensel//Office Hours//EN",
      "CALSCALE:GREGORIAN", "METHOD:PUBLISH", "BEGIN:VEVENT",
      "UID:office-hours-" + details.date + "-" + details.time.replace(":", "") + "@lukashensel.com",
      "DTSTAMP:" + icsTime(new Date()), "DTSTART:" + icsTime(start), "DTEND:" + icsTime(end),
      "SUMMARY:Office hours with Lukas Hensel",
      "LOCATION:" + icsText("Guanghua Building 2, Office 343"),
      "DESCRIPTION:" + icsText("Office hours at Guanghua Building 2, Office 343."),
      "BEGIN:VALARM", "ACTION:DISPLAY", "DESCRIPTION:Office hours with Lukas Hensel tomorrow",
      "TRIGGER:-P1D", "END:VALARM", "END:VEVENT", "END:VCALENDAR", ""
    ];
    const file = new Blob([lines.join("\r\n")], {type: "text/calendar;charset=utf-8"});
    const url = URL.createObjectURL(file);
    const link = document.createElement("a");
    link.href = url;
    link.download = "office-hours-" + details.date + "-" + details.time.replace(":", "") + ".ics";
    document.body.appendChild(link);
    link.click();
    link.remove();
    setTimeout(function () { URL.revokeObjectURL(url); }, 60000);
  });
})();
