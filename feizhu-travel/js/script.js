/* ============================================================
   飞猪旅行 · 网页元素设计
   学号：24002060415   姓名：张熙淳
   说明：
   1. 预订搜索卡的 tab 切换（机票 / 酒店 / 门票 / 度假）；
   2. 阻止演示表单提交，避免页面刷新。
   全部使用原生 JavaScript，不依赖任何第三方库。
   ============================================================ */

/* ------------------------------------------------------------
   一、预订搜索卡：四个 tab 对应四组表单
   ------------------------------------------------------------ */
(function () {
    var tabs = document.querySelectorAll("[data-booking-tab]");
    var panels = document.querySelectorAll("[data-booking-panel]");

    if (!tabs.length || !panels.length) {
        return;
    }

    function activate(name) {
        /* 当前 tab 高亮，并同步 aria-selected 供读屏软件识别 */
        tabs.forEach(function (tab) {
            var isActive = tab.getAttribute("data-booking-tab") === name;
            tab.classList.toggle("fly-booking-tab-active", isActive);
            tab.setAttribute("aria-selected", isActive ? "true" : "false");
        });

        /* 只显示与 tab 对应的那一组表单 */
        panels.forEach(function (panel) {
            panel.hidden = panel.getAttribute("data-booking-panel") !== name;
        });
    }

    tabs.forEach(function (tab) {
        tab.addEventListener("click", function () {
            activate(tab.getAttribute("data-booking-tab"));
        });
    });
})();

/* ------------------------------------------------------------
   二、演示用表单：阻止提交刷新页面
   ------------------------------------------------------------ */
(function () {
    var forms = document.querySelectorAll(".fly-search, .fly-booking-panel");

    forms.forEach(function (form) {
        form.addEventListener("submit", function (event) {
            event.preventDefault();
        });
    });
})();
