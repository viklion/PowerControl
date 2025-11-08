// 深色模式主题切换

const THEME_KEY = 'PCtheme'; // localStorage 键名

// 切换主题
function toggleTheme() {
    document.body.style.transition = "background-color 0.5s, color 0.5s";
    const currentTheme = localStorage.getItem(THEME_KEY) || 'auto';
    let nextTheme, nextTheme_cn;

    if (currentTheme === 'auto') {
        nextTheme = 'light';
        nextTheme_cn = '浅色模式';
    } else if (currentTheme === 'light') {
        nextTheme = 'dark';
        nextTheme_cn = '深色模式';
    } else {
        nextTheme = 'auto';
        nextTheme_cn = '跟随系统';
    }

    applyTheme(nextTheme);
    localStorage.setItem(THEME_KEY, nextTheme);

    swal({
        text: `主题已切换为：${nextTheme_cn}`,
        button: false,
        timer: 1500,
        className: "swal-modal-thememode",
    });
    setTimeout(() => {
        const overlay = document.querySelector('.swal-overlay');
        if (overlay) overlay.classList.add('swal-overlay-thememode');
    }, 0);
}

// 应用指定的主题
function applyTheme(theme) {
    if (theme === 'dark') {
        document.body.classList.add('dark-mode');
    } else if (theme === 'light') {
        document.body.classList.remove('dark-mode');
    } else {
        // auto 模式，跟随系统
        const isDarkMode = window.matchMedia('(prefers-color-scheme: dark)').matches;
        if (isDarkMode) {
            document.body.classList.add('dark-mode');
        } else {
            document.body.classList.remove('dark-mode');
        }
    }
}

// 页面加载时应用上次选择的主题
document.addEventListener('DOMContentLoaded', () => {
    const savedTheme = localStorage.getItem(THEME_KEY) || 'auto';
    applyTheme(savedTheme);

    const themeToggleButton = document.getElementById('theme-toggle');
    if (themeToggleButton) {
        themeToggleButton.addEventListener('click', toggleTheme);
    }
});