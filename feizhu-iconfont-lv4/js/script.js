/* ============================================================================
   飞猪旅行 · 下导航交互
   学号：24002060415    姓名：张熙淳
   ----------------------------------------------------------------------------
   下导航的 5 个 tab 全部用【字体图标】渲染，这里只负责三件事：
   1. 点击 tab 切换下方的 .fz-panel 面板（改 class + hidden 属性）
   2. 同步选中态（.fz-tabbar-item-active）与 aria-selected，方便读屏软件识别
   3. 拦截搜索框与占位链接的默认跳转，保证静态演示时不刷新页面
   ============================================================================ */
(function () {
    'use strict';

    var tabbar = document.querySelector('.fz-tabbar');
    var tabs = document.querySelectorAll('.fz-tabbar-item');
    var panels = document.querySelectorAll('.fz-panel');

    if (!tabbar || !tabs.length || !panels.length) {
        return;
    }

    /* 记住每个面板的滚动位置，来回切换时不丢进度 */
    var scrollMemory = {};

    /* 切换到指定 tab：name 与 data-tab / data-panel 对应 */
    function switchTab(name) {
        var current = document.querySelector('.fz-panel-active');
        if (current) {
            scrollMemory[current.dataset.panel] = window.pageYOffset;
        }

        Array.prototype.forEach.call(tabs, function (tab) {
            var isOn = tab.dataset.tab === name;
            tab.classList.toggle('fz-tabbar-item-active', isOn);
            tab.setAttribute('aria-selected', isOn ? 'true' : 'false');
        });

        Array.prototype.forEach.call(panels, function (panel) {
            var isOn = panel.dataset.panel === name;
            if (isOn) {
                panel.hidden = false;
                panel.classList.add('fz-panel-active');
            } else {
                panel.hidden = true;
                panel.classList.remove('fz-panel-active');
            }
        });

        var top = scrollMemory[name] || 0;
        window.scrollTo({
            top: top,
            behavior: 'smooth'
        });
    }

    /* 绑定点击事件 */
    Array.prototype.forEach.call(tabs, function (tab) {
        tab.addEventListener('click', function () {
            switchTab(tab.dataset.tab);
        });
    });

    /* 键盘左右方向键也能切换（桌面端可用，兼顾无障碍） */
    tabbar.addEventListener('keydown', function (event) {
        if (event.key !== 'ArrowLeft' && event.key !== 'ArrowRight') {
            return;
        }

        var list = Array.prototype.slice.call(tabs);
        var index = list.indexOf(document.activeElement);
        if (index === -1) {
            return;
        }

        event.preventDefault();
        var step = event.key === 'ArrowRight' ? 1 : -1;
        var next = list[(index + step + list.length) % list.length];
        next.focus();
        switchTab(next.dataset.tab);
    });

    /* 搜索框：回车时不刷新页面，只做一次占位提示 */
    var search = document.querySelector('.fz-search');
    if (search) {
        search.addEventListener('submit', function (event) {
            event.preventDefault();
            var input = search.querySelector('.fz-search-input');
            var keyword = input ? input.value.trim() : '';
            if (keyword) {
                input.value = '';
                input.placeholder = '已搜索：' + keyword + '（演示页面）';
            }
        });
    }

    /* 页面里的占位链接（href="#"）统一阻止跳转，避免点一下回到顶部 */
    document.addEventListener('click', function (event) {
        var link = event.target.closest ? event.target.closest('a[href="#"]') : null;
        if (link) {
            event.preventDefault();
        }
    });
}());
