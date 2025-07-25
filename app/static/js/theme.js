// 深色模式
// 手动切换主题的功能
function toggleTheme() {
    document.body.style.transition = "background-color 0.5s, color 0.5s";
    document.body.classList.toggle('dark-mode');
    // 保存用户选择的主题到 localStorage，确保页面刷新后保持设置
    const theme = document.body.classList.contains('dark-mode') ? 'dark' : 'light';
    localStorage.setItem('theme', theme);
}

// 检测并设置当前的主题
function detectAndApplyTheme() {
    const isDarkMode = window.matchMedia('(prefers-color-scheme: dark)').matches;
    if (isDarkMode) {
        document.body.classList.add('dark-mode');
    } else {
        document.body.classList.remove('dark-mode');
    }
}

// 页面加载时应用用户上次选择的主题
document.addEventListener('DOMContentLoaded', () => {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
        if (savedTheme === 'dark') {
            document.body.classList.add('dark-mode');
        } else {
            document.body.classList.remove('dark-mode');
        }
    } else {
        detectAndApplyTheme(); // 如果没有保存，自动检测系统主题
    }

    // 给图片添加点击事件，点击图片切换主题
    const themeToggleButton = document.getElementById('theme-toggle');
    themeToggleButton.addEventListener('click', toggleTheme);
});