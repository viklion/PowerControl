// code.html
document.addEventListener("touchstart", function () { }, true);

// 使用 ClipboardJS 实现多个代码块的复制功能
var clipboard = new ClipboardJS('.copy-btn', {
    text: function (trigger) {
        // 获取按钮对应的代码块
        var codeBlock = document.querySelector(trigger.getAttribute('data-clipboard-target'));
        // 获取代码块内容，并去掉首尾空白字符
        return codeBlock.textContent.trim();
    }
});

// 成功复制后的提示
clipboard.on('success', function (e) {
    alert('代码已复制到剪贴板!');
    e.clearSelection();
});

// 复制失败后的提示
clipboard.on('error', function (e) {
    alert('复制失败，请手动复制!');
});