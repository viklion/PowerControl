#include <winsock2.h>
#include <windows.h>
#include <shellapi.h>
#include <powrprof.h>
#include <shlwapi.h>
#include "resource.h"
#include <string>
#include <map>
#include <thread>

#pragma comment(lib, "ws2_32.lib")
#pragma comment(lib, "PowrProf.lib")
#pragma comment(lib, "Shlwapi.lib")

#define APP_NAME L"PCshutdown"
#define APP_VER L"V3.9"
#define APP_FULL APP_NAME L" " APP_VER
#define DEFAULT_PORT 17678

#define WM_TRAYICON (WM_USER + 1)
#define IDM_START 1001
#define IDM_STOP 1002
#define IDM_EXIT 1003

#define IDC_AUTORUN 2001
#define IDC_AUTOLISTEN 2002
#define IDC_HIDETRAY 2003
#define IDC_HIDEUI 2004

#define REG_PATH L"Software\\PCshutdown"
#define REG_AUTORUN L"AutoRun"
#define REG_AUTOLISTEN L"AutoListen"
#define REG_PORT L"Port"

HWND hMainWnd, hEditPort, hChkAutoRun, hChkAutoListen, hChkHideTray, hChkHideUI, hBtnStart, hBtnStop, hBtnExit;
bool listening = false;
bool windowVisible = true;
SOCKET udpSock = INVALID_SOCKET;
HANDLE hThread = NULL;
int listenPort = DEFAULT_PORT;

HICON hIconActive = NULL;
HICON hIconInactive = NULL;
// Winsock 初始化标志
bool wsaInitialized = false;

// 命令字典
const std::map<std::string, std::wstring> cmdDict = {
    {"shutdown", L"关机"},
    {"reboot", L"重启"},
    {"sleep", L"睡眠"},
    {"hibernate", L"休眠"}};

// 将 UTF-8/ANSI std::string 转为 std::wstring（线程内使用）
static std::wstring ToWString(const std::string &s)
{
    if (s.empty())
        return {};
    int len = MultiByteToWideChar(CP_UTF8, 0, s.c_str(), -1, NULL, 0);
    if (len <= 0)
        return std::wstring(s.begin(), s.end());
    std::wstring w(len, L'\0');
    MultiByteToWideChar(CP_UTF8, 0, s.c_str(), -1, &w[0], len);
    if (!w.empty() && w.back() == L'\0')
        w.pop_back();
    return w;
}

// 从收到的命令字符串中查找对应的汉字（若找不到返回空串）
static std::wstring FindCmdChinese(const std::string &d)
{
    for (const auto &p : cmdDict)
    {
        if (d.find(p.first) != std::string::npos)
            return p.second;
    }
    return L"";
}

// 前置声明：启用关机权限和获取错误字符串（定义在文件后面）
static bool EnableShutdownPrivilege(bool enable);
static std::string GetLastErrorString();

// ======== Helper functions ========

// 从注册表读取 bool
bool ReadBoolFromReg(LPCWSTR valueName)
{
    HKEY hKey;
    DWORD data = 0;
    DWORD size = sizeof(DWORD);
    if (RegOpenKeyEx(HKEY_CURRENT_USER, REG_PATH, 0, KEY_READ, &hKey) == ERROR_SUCCESS)
    {
        RegQueryValueEx(hKey, valueName, 0, NULL, (LPBYTE)&data, &size);
        RegCloseKey(hKey);
    }
    return data != 0;
}

// 写入 bool 到注册表
void WriteBoolToReg(LPCWSTR valueName, bool val)
{
    HKEY hKey;
    if (RegCreateKeyEx(HKEY_CURRENT_USER, REG_PATH, 0, NULL, 0, KEY_WRITE, NULL, &hKey, NULL) == ERROR_SUCCESS)
    {
        DWORD data = val ? 1 : 0;
        RegSetValueEx(hKey, valueName, 0, REG_DWORD, (const BYTE *)&data, sizeof(DWORD));
        RegCloseKey(hKey);
    }
}

// 读取端口
int ReadPortFromReg()
{
    HKEY hKey;
    DWORD port = DEFAULT_PORT;
    DWORD size = sizeof(DWORD);
    if (RegOpenKeyEx(HKEY_CURRENT_USER, REG_PATH, 0, KEY_READ, &hKey) == ERROR_SUCCESS)
    {
        RegQueryValueEx(hKey, REG_PORT, 0, NULL, (LPBYTE)&port, &size);
        RegCloseKey(hKey);
    }
    return port;
}

// 保存端口
void WritePortToReg(int port)
{
    HKEY hKey;
    if (RegCreateKeyEx(HKEY_CURRENT_USER, REG_PATH, 0, NULL, 0, KEY_WRITE, NULL, &hKey, NULL) == ERROR_SUCCESS)
    {
        RegSetValueEx(hKey, REG_PORT, 0, REG_DWORD, (const BYTE *)&port, sizeof(DWORD));
        RegCloseKey(hKey);
    }
}

// Windows 通知
void ShowNotification(LPCWSTR title, LPCWSTR msg)
{
    // 如果没有主窗口句柄，则退回到 MessageBox
    if (!hMainWnd)
    {
        MessageBox(NULL, msg, title, MB_OK | MB_ICONINFORMATION);
        return;
    }

    std::wstring wtitle = title ? title : L"";
    std::wstring wmsg = msg ? msg : L"";

    // 始终使用临时托盘图标来显示通知
    HICON icon = NULL;
    if (hIconActive)
        icon = hIconActive;
    else
        icon = (HICON)LoadImage(GetModuleHandle(NULL), MAKEINTRESOURCE(IDI_APPICON), IMAGE_ICON, 48, 48, LR_SHARED | LR_DEFAULTCOLOR);

    // 在后台线程中处理通知
    std::thread([wtitle, wmsg, icon]() {
        NOTIFYICONDATA nid{};
        nid.cbSize = sizeof(nid);
        nid.hWnd = hMainWnd;

        // 临时 ID，避免与主托盘图标冲突
        nid.uID = 0xBEEF;

        // 填充显示文本
        wcscpy_s(nid.szInfoTitle, wtitle.c_str());
        wcscpy_s(nid.szInfo, wmsg.c_str());
        nid.uTimeout = 2000;

        // 使用图标字段和气泡图标字段
        nid.uFlags = NIF_INFO;
        if (icon)
        {
            nid.hIcon = icon;
            #ifdef _WIN32_WINNT
                // 如果结构支持 hBalloonIcon（较新 SDK），则设置它以保证气泡使用彩色图标
                nid.uFlags |= NIF_ICON;
                #if defined(NIM_ADD)
                    // 尝试设置 hBalloonIcon 成员（在较新 Windows SDK 中可用）
                    nid.hBalloonIcon = icon;
                #endif
            #endif
        }

        // 调用
        Shell_NotifyIcon(NIM_ADD, &nid);

        // 删除临时图标
        // Sleep(500);
        Shell_NotifyIcon(NIM_DELETE, &nid);
    }).detach();
}

// 更新托盘图标和按钮状态
void UpdateTrayAndButtons(bool active)
{
    NOTIFYICONDATA nid{};
    nid.cbSize = sizeof(nid);
    nid.hWnd = hMainWnd;
    nid.uID = 1;
    nid.uFlags = NIF_ICON | NIF_TIP;
    nid.uCallbackMessage = WM_TRAYICON;
    nid.hIcon = active ? hIconActive : hIconInactive;
    wchar_t tip[128];
    wcscpy_s(tip, 128, APP_FULL);
    wcscat_s(tip, 128, active ? L"（监听中）" : L"（未监听）");
    wcscpy_s(nid.szTip, tip);
    Shell_NotifyIcon(NIM_MODIFY, &nid);

    // 按钮状态
    EnableWindow(hBtnStart, !active);
    EnableWindow(hBtnStop, active);
}

// ======== 监听线程占位 ========
DWORD WINAPI ListenThread(LPVOID lpParam)
{
    sockaddr_in addr{};
    char buf[512];

    udpSock = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = INADDR_ANY;
    addr.sin_port = htons(listenPort);

    bind(udpSock, (sockaddr *)&addr, sizeof(addr));

    while (listening)
    {
        sockaddr_in remote{};
        int remoteLen = sizeof(remote);
        int len = recvfrom(udpSock, buf, sizeof(buf) - 1, 0, (sockaddr *)&remote, &remoteLen);
        if (len <= 0)
            continue;
        buf[len] = 0;

        std::string d(buf);
        int t = 0;
        sscanf_s(d.c_str(), "%*[^0-9]%d", &t);

        // 回复
        try
        {
            const char *ack = "succeeded";
            sendto(udpSock, ack, (int)strlen(ack), 0, (sockaddr *)&remote, remoteLen);
        }
        catch (...)
        {
            // 忽略发送 ack 的错误
        }

        // 查找命令对应的中文
        std::wstring cmdZh = FindCmdChinese(d);
        std::wstring wd = ToWString(d);
        wchar_t notice[256];
        if (!cmdZh.empty())
        {
            swprintf_s(notice, 256, L"收到指令，将于%d秒后执行：%s", t, cmdZh.c_str());
        }
        else
        {
            swprintf_s(notice, 256, L"收到指令，将于%d秒后执行：%s", t, wd.c_str());
        }
        // 在接收后通知
        ShowNotification(APP_NAME, notice);

        // 执行指令
        std::string resp;
        bool executed = false;
        try
        {
            if (d.find("shutdown") != std::string::npos)
            {
                EnableShutdownPrivilege(true);
                BOOL r = InitiateSystemShutdownEx(NULL, NULL, t, TRUE, FALSE, 0);
                executed = (r != 0);
                if (!executed)
                {
                    std::string err = GetLastErrorString();
                    resp = std::string("failed:InitiateSystemShutdownEx returned 0") + (err.empty() ? "" : std::string(":") + err);
                }
            }
            else if (d.find("reboot") != std::string::npos)
            {
                EnableShutdownPrivilege(true);
                BOOL r = InitiateSystemShutdownEx(NULL, NULL, t, TRUE, TRUE, 0);
                executed = (r != 0);
                if (!executed)
                {
                    std::string err = GetLastErrorString();
                    resp = std::string("failed:InitiateSystemShutdownEx returned 0") + (err.empty() ? "" : std::string(":") + err);
                }
            }
            else if (d.find("sleep") != std::string::npos)
            {
                Sleep(t * 1000);
                BOOL r = SetSuspendState(FALSE, TRUE, FALSE);
                executed = (r != 0);
                if (!executed)
                {
                    std::string err = GetLastErrorString();
                    resp = std::string("failed:SetSuspendState returned 0") + (err.empty() ? "" : std::string(":") + err);
                }
            }
            else if (d.find("hibernate") != std::string::npos)
            {
                Sleep(t * 1000);
                BOOL r = SetSuspendState(TRUE, TRUE, FALSE);
                executed = (r != 0);
                if (!executed)
                {
                    std::string err = GetLastErrorString();
                    resp = std::string("failed:SetSuspendState returned 0") + (err.empty() ? "" : std::string(":") + err);
                }
            }
            else
            {
                resp = "failed:unknown command";
            }

            if (resp.empty())
                resp = executed ? "succeeded" : "failed:unknown error";
        }
        catch (const std::exception &e)
        {
            resp = std::string("failed:") + e.what();
        }
        catch (...)
        {
            if (resp.empty())
                resp = "failed:exception";
        }

        // 如果执行失败，显示通知
        if (resp.rfind("failed:", 0) == 0)
        {
            std::wstring wresp = ToWString(resp);
            wchar_t failNotice[256];
            swprintf_s(failNotice, 256, L"指令执行失败：%s", wresp.c_str());
            ShowNotification(APP_NAME, failNotice);
        }
    }
    closesocket(udpSock);
    return 0;
}

bool IsPortAvailable(int port)
{
    // 确保 Winsock 已初始化
    if (!wsaInitialized)
    {
        WSADATA wsaData;
        if (WSAStartup(MAKEWORD(2, 2), &wsaData) != 0)
        {
            return false;
        }
        wsaInitialized = true;
    }

    SOCKET s = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
    if (s == INVALID_SOCKET)
        return false;
    sockaddr_in addr{};
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = INADDR_ANY;
    addr.sin_port = htons(port);
    bool ok = bind(s, (sockaddr *)&addr, sizeof(addr)) == 0;
    closesocket(s);
    return ok;
}

void StartListen()
{
    if (listening)
        return;
    wchar_t buf[16];
    GetWindowText(hEditPort, buf, 16);
    listenPort = _wtoi(buf);
    WritePortToReg(listenPort);

    // 检查端口占用
    if (!IsPortAvailable(listenPort))
    {
        MessageBox(hMainWnd, L"端口已被占用", APP_NAME, MB_ICONERROR);
        return;
    }

    // 禁用端口编辑框
    EnableWindow(hEditPort, FALSE);

    // 开始线程
    listening = true;
    UpdateTrayAndButtons(true);
    wchar_t msgStart[128];
    swprintf_s(msgStart, 128, L"开始监听端口：%d", listenPort);
    ShowNotification(APP_NAME, msgStart);
    hThread = CreateThread(NULL, 0, ListenThread, NULL, 0, NULL);
}

void StopListen()
{
    if (!listening)
        return;
    listening = false;
    UpdateTrayAndButtons(false);
    // 启用端口编辑框
    EnableWindow(hEditPort, TRUE);
    wchar_t msgStop[128];
    swprintf_s(msgStop, 128, L"停止监听端口：%d", listenPort);
    ShowNotification(APP_NAME, msgStop);
    if (hThread)
    {
        TerminateThread(hThread, 0);
        CloseHandle(hThread);
        hThread = NULL;
    }

    // 端口释放
    if (udpSock != INVALID_SOCKET)
    {
        closesocket(udpSock);
        udpSock = INVALID_SOCKET;
    }

    // 清理 Winsock
    if (wsaInitialized)
    {
        WSACleanup();
        wsaInitialized = false;
    }
}

// 设置开机自启
void SetAutoRun(bool enable)
{
    HKEY hKey;
    if (RegCreateKeyEx(HKEY_CURRENT_USER, L"Software\\Microsoft\\Windows\\CurrentVersion\\Run", 0, NULL, 0, KEY_WRITE, NULL, &hKey, NULL) == ERROR_SUCCESS)
    {
        if (enable)
        {
            wchar_t path[MAX_PATH];
            GetModuleFileName(NULL, path, MAX_PATH);
            RegSetValueEx(hKey, APP_NAME, 0, REG_SZ, (const BYTE *)path, (wcslen(path) + 1) * sizeof(wchar_t));
        }
        else
        {
            RegDeleteValue(hKey, APP_NAME);
        }
        RegCloseKey(hKey);
    }
    WriteBoolToReg(REG_AUTORUN, enable);
}

// 启用或禁用 SE_SHUTDOWN_NAME 权限
static bool EnableShutdownPrivilege(bool enable)
{
    HANDLE hToken = NULL;
    if (!OpenProcessToken(GetCurrentProcess(), TOKEN_ADJUST_PRIVILEGES | TOKEN_QUERY, &hToken))
        return false;
    TOKEN_PRIVILEGES tp = {0};
    LUID luid;
    if (!LookupPrivilegeValue(NULL, SE_SHUTDOWN_NAME, &luid))
    {
        CloseHandle(hToken);
        return false;
    }
    tp.PrivilegeCount = 1;
    tp.Privileges[0].Luid = luid;
    tp.Privileges[0].Attributes = enable ? SE_PRIVILEGE_ENABLED : 0;
    AdjustTokenPrivileges(hToken, FALSE, &tp, sizeof(tp), NULL, NULL);
    bool ok = (GetLastError() == ERROR_SUCCESS);
    CloseHandle(hToken);
    return ok;
}

// 获取最后一次错误的字符串描述（ANSI）
static std::string GetLastErrorString()
{
    DWORD err = GetLastError();
    if (err == 0)
        return std::string();
    char *buf = NULL;
    DWORD len = FormatMessageA(FORMAT_MESSAGE_ALLOCATE_BUFFER | FORMAT_MESSAGE_FROM_SYSTEM | FORMAT_MESSAGE_IGNORE_INSERTS,
                               NULL, err, MAKELANGID(LANG_NEUTRAL, SUBLANG_DEFAULT), (LPSTR)&buf, 0, NULL);
    std::string s;
    if (len && buf)
    {
        // Trim trailing newline characters
        while (len > 0 && (buf[len - 1] == '\n' || buf[len - 1] == '\r'))
        {
            buf[len - 1] = '\0';
            len--;
        }
        s = buf;
        LocalFree(buf);
    }
    return s;
}

UINT gTaskbarRestartMsg = 0;

// ======== 窗口回调 ========
LRESULT CALLBACK WndProc(HWND hWnd, UINT msg, WPARAM wParam, LPARAM lParam)
{
    // Explorer 重启后重建托盘图标
    if (gTaskbarRestartMsg != 0 && msg == gTaskbarRestartMsg)
    {
        bool hideTray = SendMessage(hChkHideTray, BM_GETCHECK, 0, 0) == BST_CHECKED;
        if (!hideTray)
        {
            NOTIFYICONDATA nid{};
            nid.cbSize = sizeof(nid);
            nid.hWnd = hWnd;
            nid.uID = 1;
            nid.uFlags = NIF_ICON | NIF_MESSAGE | NIF_TIP;
            nid.uCallbackMessage = WM_TRAYICON;
            nid.hIcon = listening ? hIconActive : hIconInactive;
            wcscpy_s(nid.szTip, APP_FULL);
            Shell_NotifyIcon(NIM_ADD, &nid);
        }
        return 0;
    }

    switch (msg)
    {
    case WM_CREATE:
    {
        hMainWnd = hWnd;

        // 注册 TaskbarCreated 消息，用于检测资源管理器重启
        gTaskbarRestartMsg = RegisterWindowMessageW(L"TaskbarCreated");

        // UI 布局
        HFONT hFontTitle = CreateFont(24, 0, 0, 0, FW_BOLD, FALSE, FALSE, FALSE, DEFAULT_CHARSET, OUT_DEFAULT_PRECIS, CLIP_DEFAULT_PRECIS, DEFAULT_QUALITY, DEFAULT_PITCH | FF_SWISS, L"Arial");
        HWND hTitle = CreateWindow(L"STATIC", APP_FULL, WS_CHILD | WS_VISIBLE | SS_CENTER,
                                   0, 20, 600, 30, hWnd, NULL, NULL, NULL);
        SendMessage(hTitle, WM_SETFONT, (WPARAM)hFontTitle, TRUE);

        CreateWindow(L"STATIC", L"by viklion", WS_CHILD | WS_VISIBLE,
                     510, 46, 100, 24, hWnd, NULL, NULL, NULL);

        HFONT hFontModern = CreateFont(20, 0, 0, 0, FW_NORMAL, FALSE, FALSE, FALSE, DEFAULT_CHARSET, OUT_DEFAULT_PRECIS, CLIP_DEFAULT_PRECIS, DEFAULT_QUALITY, DEFAULT_PITCH | FF_SWISS, L"Segoe UI");

        // 添加分组框
        HWND hGroupSettings = CreateWindow(L"BUTTON", L"设置", WS_CHILD | WS_VISIBLE | BS_GROUPBOX,
                                           20, 60, 560, 120, hWnd, NULL, NULL, NULL);
        SendMessage(hGroupSettings, WM_SETFONT, (WPARAM)hFontModern, TRUE);

        HWND hGroupActions = CreateWindow(L"BUTTON", L"操作", WS_CHILD | WS_VISIBLE | BS_GROUPBOX,
                                          20, 180, 560, 80, hWnd, NULL, NULL, NULL);
        SendMessage(hGroupActions, WM_SETFONT, (WPARAM)hFontModern, TRUE);

        // 调整控件布局到分组框内
        HWND hLabelPort = CreateWindow(L"STATIC", L"监听端口(UDP)：", WS_CHILD | WS_VISIBLE,
                                       40, 90, 150, 30, hWnd, NULL, NULL, NULL);
        SendMessage(hLabelPort, WM_SETFONT, (WPARAM)hFontModern, TRUE);
        hEditPort = CreateWindow(L"EDIT", L"17678", WS_CHILD | WS_VISIBLE | WS_BORDER,
                                 160, 86, 120, 30, hWnd, NULL, NULL, NULL);
        SendMessage(hEditPort, WM_SETFONT, (WPARAM)hFontModern, TRUE);

        hChkAutoRun = CreateWindow(L"BUTTON", L"开机自动启动", WS_CHILD | WS_VISIBLE | BS_AUTOCHECKBOX,
                                   40, 130, 110, 30, hWnd, (HMENU)IDC_AUTORUN, NULL, NULL);
        SendMessage(hChkAutoRun, WM_SETFONT, (WPARAM)hFontModern, TRUE);
        hChkAutoListen = CreateWindow(L"BUTTON", L"启动后自动监听", WS_CHILD | WS_VISIBLE | BS_AUTOCHECKBOX,
                                      160, 130, 120, 30, hWnd, (HMENU)IDC_AUTOLISTEN, NULL, NULL);
        SendMessage(hChkAutoListen, WM_SETFONT, (WPARAM)hFontModern, TRUE);
        hChkHideTray = CreateWindow(L"BUTTON", L"隐藏托盘图标", WS_CHILD | WS_VISIBLE | BS_AUTOCHECKBOX,
                                    456, 130, 110, 30, hWnd, (HMENU)IDC_HIDETRAY, NULL, NULL);
        SendMessage(hChkHideTray, WM_SETFONT, (WPARAM)hFontModern, TRUE);

        hChkHideUI = CreateWindow(L"BUTTON", L"启动时不显示主界面", WS_CHILD | WS_VISIBLE | BS_AUTOCHECKBOX,
                                   296, 130, 150, 30, hWnd, (HMENU)IDC_HIDEUI, NULL, NULL);
        SendMessage(hChkHideUI, WM_SETFONT, (WPARAM)hFontModern, TRUE);

        // 同步复选框状态，启动时不显示主界面
        if (ReadBoolFromReg(L"HideUI")) {
            SendMessage(hChkHideUI, BM_SETCHECK, BST_CHECKED, 0);
        }

        // 同步复选框状态，隐藏托盘图标
        bool hideTray = ReadBoolFromReg(L"HideTray");
        if (hideTray) {
            SendMessage(hChkHideTray, BM_SETCHECK, BST_CHECKED, 0);
        }

        // 判断是否启动时隐藏主界面
        if (ReadBoolFromReg(L"HideUI")) {
            ShowWindow(hWnd, SW_HIDE);
            windowVisible = false;
        }

        hBtnStart = CreateWindow(L"BUTTON", L"开始监听", WS_CHILD | WS_VISIBLE | BS_PUSHBUTTON | BS_FLAT,
                                 40, 210, 100, 30, hWnd, (HMENU)IDM_START, NULL, NULL);
        SendMessage(hBtnStart, WM_SETFONT, (WPARAM)hFontModern, TRUE);
        hBtnStop = CreateWindow(L"BUTTON", L"停止监听", WS_CHILD | WS_VISIBLE | BS_PUSHBUTTON | BS_FLAT,
                                160, 210, 100, 30, hWnd, (HMENU)IDM_STOP, NULL, NULL);
        SendMessage(hBtnStop, WM_SETFONT, (WPARAM)hFontModern, TRUE);

        // 新增退出程序按钮（不改变现有布局）
        hBtnExit = CreateWindow(L"BUTTON", L"退出程序", WS_CHILD | WS_VISIBLE | BS_PUSHBUTTON | BS_FLAT,
                                460, 210, 100, 30, hWnd, (HMENU)IDM_EXIT, NULL, NULL);
        SendMessage(hBtnExit, WM_SETFONT, (WPARAM)hFontModern, TRUE);

        hIconActive = LoadIcon(GetModuleHandle(NULL), MAKEINTRESOURCE(IDI_APPICON));
        hIconInactive = LoadIcon(GetModuleHandle(NULL), MAKEINTRESOURCE(IDI_APPICON_GRAY));

        NOTIFYICONDATA nid{};
        nid.cbSize = sizeof(nid);
        nid.hWnd = hWnd;
        nid.uID = 1;
        nid.uFlags = NIF_ICON | NIF_MESSAGE | NIF_TIP;
        nid.uCallbackMessage = WM_TRAYICON;
        nid.hIcon = hIconInactive;
        wchar_t initTip[128];
        wcscpy_s(initTip, 128, APP_FULL);
        wcscat_s(initTip, 128, L"（未监听）");
        wcscpy_s(nid.szTip, initTip);
        // 只有在未设置隐藏托盘图标时才添加托盘图标
        if (!hideTray) {
            Shell_NotifyIcon(NIM_ADD, &nid);
        }

        // 加载上次配置
        listenPort = ReadPortFromReg();
        wchar_t buf[16];
        wsprintf(buf, L"%d", listenPort);
        SetWindowText(hEditPort, buf);

        if (ReadBoolFromReg(REG_AUTORUN))
            SendMessage(hChkAutoRun, BM_SETCHECK, BST_CHECKED, 0);
        if (ReadBoolFromReg(REG_AUTOLISTEN))
        {
            SendMessage(hChkAutoListen, BM_SETCHECK, BST_CHECKED, 0);
            StartListen();
        }

        UpdateTrayAndButtons(listening);
        break;
    }
    case WM_COMMAND:
        if (LOWORD(wParam) == IDM_START)
            StartListen();
        else if (LOWORD(wParam) == IDM_STOP)
            StopListen();
        else if (LOWORD(wParam) == IDC_AUTORUN)
            SetAutoRun(SendMessage(hChkAutoRun, BM_GETCHECK, 0, 0) == BST_CHECKED);
        else if (LOWORD(wParam) == IDC_AUTOLISTEN)
        {
            // 保存到注册表
            bool enable = SendMessage(hChkAutoListen, BM_GETCHECK, 0, 0) == BST_CHECKED;
            WriteBoolToReg(REG_AUTOLISTEN, enable);
        }
        else if (LOWORD(wParam) == IDC_HIDETRAY)
        {
            bool hideTray = SendMessage(hChkHideTray, BM_GETCHECK, 0, 0) == BST_CHECKED;
            WriteBoolToReg(L"HideTray", hideTray);
            NOTIFYICONDATA nid = {sizeof(NOTIFYICONDATA), hWnd, 1};
            if (hideTray)
            {
                Shell_NotifyIcon(NIM_DELETE, &nid);
            }
            else
            {
                nid.uFlags = NIF_ICON | NIF_MESSAGE | NIF_TIP;
                nid.uCallbackMessage = WM_TRAYICON;
                nid.hIcon = listening ? hIconActive : hIconInactive;
                wcscpy_s(nid.szTip, APP_FULL);
                Shell_NotifyIcon(NIM_ADD, &nid);
            }
        }
        else if (LOWORD(wParam) == IDC_HIDEUI)
        {
            bool hideUI = SendMessage(hChkHideUI, BM_GETCHECK, 0, 0) == BST_CHECKED;
            WriteBoolToReg(L"HideUI", hideUI);
            // 仅在下次启动时生效
        }
        else if (LOWORD(wParam) == IDM_EXIT)
            DestroyWindow(hWnd);
        break;

    case WM_CLOSE:
        // 保存 HideUI 和 HideTray 状态
        if (hChkHideUI) {
            bool hideUI = SendMessage(hChkHideUI, BM_GETCHECK, 0, 0) == BST_CHECKED;
            WriteBoolToReg(L"HideUI", hideUI);
        }
        if (hChkHideTray) {
            bool hideTray = SendMessage(hChkHideTray, BM_GETCHECK, 0, 0) == BST_CHECKED;
            WriteBoolToReg(L"HideTray", hideTray);
        }
        ShowWindow(hWnd, SW_HIDE);
        windowVisible = false;
        return 0;

    case WM_SIZE:
        break;

    // UI界面添加重绘逻辑
    case WM_PAINT:
    {
        PAINTSTRUCT ps;
        HDC hdc = BeginPaint(hWnd, &ps);
        RECT rect;
        GetClientRect(hWnd, &rect);
        FillRect(hdc, &rect, (HBRUSH)GetStockObject(WHITE_BRUSH)); // 使用白色背景
        EndPaint(hWnd, &ps);
        break;
    }

    // 设置控件背景色为白色
    case WM_CTLCOLORSTATIC:
    case WM_CTLCOLOREDIT:
    case WM_CTLCOLORBTN:
    {
        HDC hdc = (HDC)wParam;
        SetBkColor(hdc, RGB(255, 255, 255)); // 设置背景色为白色
        SetTextColor(hdc, RGB(0, 0, 0));     // 设置文本颜色为黑色
        return (LRESULT)GetStockObject(WHITE_BRUSH);
    }

    case WM_TRAYICON:
        if (lParam == WM_LBUTTONUP)
        {
            ShowWindow(hWnd, windowVisible ? SW_HIDE : SW_SHOW);
            windowVisible = !windowVisible;
        }
        else if (lParam == WM_RBUTTONUP)
        {
            HMENU m = CreatePopupMenu();
            AppendMenu(m, MF_GRAYED, 0, APP_FULL);
            AppendMenu(m, MF_GRAYED, 0, L"by viklion");
            AppendMenu(m, MF_SEPARATOR, 0, NULL);

            // 获取所有监听IP地址
            AppendMenu(m, MF_GRAYED, 0, L"监听ip：");
            char hostname[256];
            if (gethostname(hostname, sizeof(hostname)) == 0)
            {
                struct hostent *host = gethostbyname(hostname);
                if (host)
                {
                    for (int i = 0; host->h_addr_list[i] && i < 10; ++i)
                    {
                        struct in_addr addr;
                        memcpy(&addr, host->h_addr_list[i], sizeof(struct in_addr));
                        wchar_t ip[16];
                        MultiByteToWideChar(CP_ACP, 0, inet_ntoa(addr), -1, ip, sizeof(ip) / sizeof(wchar_t));
                        AppendMenu(m, MF_GRAYED, 0, ip);
                    }
                }
            }

            AppendMenu(m, MF_SEPARATOR, 0, NULL);
            AppendMenu(m, listening ? MF_GRAYED : MF_STRING, IDM_START, L"开始监听");
            AppendMenu(m, listening ? MF_STRING : MF_GRAYED, IDM_STOP, L"停止监听");
            AppendMenu(m, MF_STRING, IDM_EXIT, L"退出");
            POINT p;
            GetCursorPos(&p);
            SetForegroundWindow(hWnd);
            TrackPopupMenu(m, TPM_RIGHTBUTTON, p.x, p.y, 0, hWnd, NULL);
            DestroyMenu(m);
        }
        break;

    case WM_DESTROY:
    {
        // 保存 HideUI 和 HideTray 状态
        if (hChkHideUI) {
            bool hideUI = SendMessage(hChkHideUI, BM_GETCHECK, 0, 0) == BST_CHECKED;
            WriteBoolToReg(L"HideUI", hideUI);
        }
        if (hChkHideTray) {
            bool hideTray = SendMessage(hChkHideTray, BM_GETCHECK, 0, 0) == BST_CHECKED;
            WriteBoolToReg(L"HideTray", hideTray);
        }

        NOTIFYICONDATA nid = {sizeof(NOTIFYICONDATA), hWnd, 1};
        Shell_NotifyIcon(NIM_DELETE, &nid);
        // 退出前清理 Winsock
        if (wsaInitialized)
        {
            WSACleanup();
            wsaInitialized = false;
        }
        PostQuitMessage(0);
        break;
    }
    }
    return DefWindowProc(hWnd, msg, wParam, lParam);
}

// ======== WinMain ========
int WINAPI wWinMain(HINSTANCE hInst, HINSTANCE hPrev, PWSTR lpCmdLine, int nCmdShow)
{
    // 单实例检查
    HANDLE hInstanceMutex = CreateMutexW(NULL, FALSE, L"PCshutdown_single_instance_mutex_v1");
    if (hInstanceMutex && GetLastError() == ERROR_ALREADY_EXISTS)
    {
        // 找到已经运行的窗口并激活
        HWND other = FindWindow(APP_NAME, APP_NAME);
        if (other)
        {
            ShowWindow(other, SW_SHOW);
            SetForegroundWindow(other);
        }
        // 关闭本次创建的句柄并退出
        if (hInstanceMutex)
            CloseHandle(hInstanceMutex);
        return 0;
    }

    WNDCLASS wc = {};
    wc.lpfnWndProc = WndProc;
    wc.hInstance = hInst;
    wc.lpszClassName = APP_NAME;
    wc.hIcon = LoadIcon(hInst, MAKEINTRESOURCE(IDI_APPICON));
    RegisterClass(&wc);

    // 禁止手动调整窗口大小
    HWND hwnd = CreateWindow(APP_NAME, APP_NAME, WS_OVERLAPPED | WS_CAPTION | WS_SYSMENU,
                             CW_USEDEFAULT, CW_USEDEFAULT, 600, 320, NULL, NULL, hInst, NULL);
    // 启动时是否显示窗口
    if (ReadBoolFromReg(L"HideUI")) {
        ShowWindow(hwnd, SW_HIDE);
        windowVisible = false;
    } else {
        ShowWindow(hwnd, nCmdShow);
        windowVisible = true;
    }

    MSG msg;
    while (GetMessage(&msg, NULL, 0, 0))
    {
        TranslateMessage(&msg);
        DispatchMessage(&msg);
    }

    // 程序退出前释放互斥体句柄（保留到此处以维持单实例）
    if (hInstanceMutex)
    {
        CloseHandle(hInstanceMutex);
        hInstanceMutex = NULL;
    }
    return 0;
}