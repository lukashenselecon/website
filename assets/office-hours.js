/* Availability is requested only after the name and PKU email step. */
(function () {
  "use strict";
  const root = document.getElementById("office-booking");
  if (!root) return;
  const zh = root.dataset.lang === "zh";
  const identity = document.getElementById("identity-form");
  const identityStatus = document.getElementById("identity-status");
  const step = document.getElementById("booking-step");
  const booking = document.getElementById("booking-form");
  const bookingStatus = document.getElementById("booking-status");
  const slotsBox = document.getElementById("booking-slots");
  const receipt = document.getElementById("booking-receipt");
  const receiptKey = "office-hours-confirmed-booking";
  let token = "";

  const words = zh ? {
    loading: "正在查询可预约时间……", noSlots: "这些日期暂时没有可预约的时间。",
    unavailable: "已预约", blocked: "当天不可预约", choose: "请先选择一个时间。",
    fileCount: "最多可附加 3 个文件。", fileSize: "每个文件不能超过 10 MB。",
    sending: "正在提交预约……", failed: "请求未完成，请重试。",
    confirmed: "预约成功", location: "地点", save: "可以记下预约时间；系统不会另行发送确认邮件。",
    beijing: "北京时间"
  } : {
    loading: "Checking available times…", noSlots: "No appointments are available on these dates.",
    unavailable: "Booked", blocked: "No office hours", choose: "Choose a time first.",
    fileCount: "Attach at most 3 files.", fileSize: "Each file must be 10 MB or smaller.",
    sending: "Submitting your booking…", failed: "The request did not finish. Please try again.",
    confirmed: "Booking confirmed", location: "Location", save: "You may wish to note the time. We won't send a separate confirmation email.",
    beijing: "Beijing time"
  };
  const chineseErrors = {
    identity: "请输入姓名和北京大学邮箱。", rate: "尝试次数过多，请稍后再试。",
    purpose: "请填写会面目的，最多 2000 字。", unavailable: "该时间已不可预约，请重新选择。",
    file_count: "最多可附加 3 个文件。", file: "请上传有效的 PDF、DOCX、PNG 或 JPEG 文件，每个不超过 10 MB。",
    taken: "该时间刚被他人预约，请选择其他时间。", failed: "预约未成功，请重试。"
  };

  function showStatus(element, message, error) {
    element.textContent = message;
    element.classList.toggle("error", Boolean(error));
  }

  async function api(path, options) {
    const response = await fetch("/api/office-hours/" + path, Object.assign({
      credentials: "same-origin", cache: "no-store"
    }, options));
    let data;
    try { data = await response.json(); } catch (_) { data = {}; }
    if (!response.ok) throw new Error((zh && chineseErrors[data.code]) || data.error || words.failed);
    return data;
  }

  function dateLabel(iso) {
    const day = new Date(iso + "T12:00:00+08:00");
    return new Intl.DateTimeFormat(zh ? "zh-CN" : "en-GB", {
      weekday: "long", year: "numeric", month: "long", day: "numeric", timeZone: "Asia/Shanghai"
    }).format(day);
  }

  function renderDates(dates) {
    slotsBox.replaceChildren();
    let available = 0;
    dates.forEach(function (day) {
      const fieldset = document.createElement("fieldset");
      fieldset.className = "booking-day";
      const legend = document.createElement("legend");
      legend.textContent = dateLabel(day.date);
      fieldset.appendChild(legend);
      if (day.blocked) {
        const note = document.createElement("p");
        note.className = "meta";
        note.textContent = words.blocked;
        fieldset.appendChild(note);
      } else {
        const grid = document.createElement("div");
        grid.className = "booking-grid";
        day.slots.forEach(function (slot) {
          const label = document.createElement("label");
          label.className = "booking-slot" + (slot.available ? "" : " taken");
          const radio = document.createElement("input");
          radio.type = "radio";
          radio.name = "slot";
          radio.value = day.date + "|" + slot.time;
          radio.disabled = !slot.available;
          if (slot.available) available += 1;
          const time = document.createElement("span");
          time.textContent = slot.time + "–" + slot.end;
          label.append(radio, time);
          if (!slot.available) {
            const state = document.createElement("small");
            state.textContent = words.unavailable;
            label.appendChild(state);
          }
          grid.appendChild(label);
        });
        fieldset.appendChild(grid);
      }
      slotsBox.appendChild(fieldset);
    });
    if (!available) {
      const note = document.createElement("p");
      note.className = "meta";
      note.textContent = words.noSlots;
      slotsBox.appendChild(note);
    }
  }

  identity.addEventListener("submit", async function (event) {
    event.preventDefault();
    const button = identity.querySelector("button");
    button.disabled = true;
    showStatus(identityStatus, words.loading, false);
    try {
      const result = await api("start", {
        method: "POST", headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
          name: identity.elements.name.value,
          email: identity.elements.email.value,
          website: identity.elements.website.value
        })
      });
      token = result.token;
      renderDates(result.dates);
      identity.hidden = true;
      step.hidden = false;
      showStatus(identityStatus, "", false);
      step.scrollIntoView({behavior: "smooth", block: "start"});
    } catch (error) {
      showStatus(identityStatus, error.message || words.failed, true);
    } finally {
      button.disabled = false;
    }
  });

  booking.addEventListener("submit", async function (event) {
    event.preventDefault();
    const selected = booking.querySelector('input[name="slot"]:checked');
    if (!selected) { showStatus(bookingStatus, words.choose, true); return; }
    const files = document.getElementById("meeting-files").files;
    if (files.length > 3) { showStatus(bookingStatus, words.fileCount, true); return; }
    if (Array.from(files).some(file => file.size > 10 * 1024 * 1024)) {
      showStatus(bookingStatus, words.fileSize, true); return;
    }
    const button = booking.querySelector("button");
    button.disabled = true;
    showStatus(bookingStatus, words.sending, false);
    const parts = selected.value.split("|");
    const data = new FormData();
    data.append("token", token);
    data.append("date", parts[0]);
    data.append("time", parts[1]);
    data.append("purpose", document.getElementById("meeting-purpose").value);
    Array.from(files).forEach(file => data.append("attachments", file));
    let completed = false;
    try {
      const result = await api("book", {method: "POST", body: data});
      completed = true;
      try {
        sessionStorage.setItem(receiptKey, JSON.stringify({
          date: result.date, time: result.time,
          end: result.end, location: result.location, location_zh: result.location_zh
        }));
        window.location.assign((zh ? "/zh" : "") + "/office-hours-confirmed");
        return;
      } catch (_) { /* Keep the receipt visible here if browser storage is unavailable. */ }
      step.hidden = true;
      const heading = document.createElement("h2");
      heading.textContent = words.confirmed;
      const details = document.createElement("p");
      details.textContent = dateLabel(result.date) + ", " + result.time + "–" + result.end + " · " + words.beijing;
      const location = document.createElement("p");
      location.textContent = words.location + ": " + (zh ? result.location_zh : result.location);
      const save = document.createElement("p");
      save.className = "meta";
      save.textContent = words.save;
      receipt.replaceChildren(heading, details, location, save);
      receipt.hidden = false;
      receipt.scrollIntoView({behavior: "smooth", block: "start"});
    } catch (error) {
      showStatus(bookingStatus, error.message || words.failed, true);
      try {
        const refreshed = await api("slots", {
          method: "POST", headers: {"Content-Type": "application/json"},
          body: JSON.stringify({token: token})
        });
        renderDates(refreshed.dates);
      } catch (_) { /* The original error remains visible. */ }
    } finally {
      if (!completed) button.disabled = false;
    }
  });
})();
