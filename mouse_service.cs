using System;
using System.Runtime.InteropServices;
using System.Globalization;

class MouseService {
    [DllImport("user32.dll")]
    static extern bool SetCursorPos(int X, int Y);

    [DllImport("user32.dll")]
    static extern void mouse_event(uint dwFlags, uint dx, uint dy, uint dwData, UIntPtr dwExtraInfo);

    const uint MOUSEEVENTF_LEFTDOWN   = 0x0002;
    const uint MOUSEEVENTF_LEFTUP     = 0x0004;
    const uint MOUSEEVENTF_RIGHTDOWN  = 0x0008;
    const uint MOUSEEVENTF_RIGHTUP    = 0x0010;
    const uint MOUSEEVENTF_MIDDLEDOWN = 0x0020;
    const uint MOUSEEVENTF_MIDDLEUP   = 0x0040;
    const uint MOUSEEVENTF_WHEEL      = 0x0800;

    static void Main(string[] args) {
        Console.OutputEncoding = System.Text.Encoding.UTF8;
        Console.WriteLine("READY");
        string line;
        while ((line = Console.ReadLine()) != null) {
            line = line.Trim();
            if (line.Length == 0) continue;
            string[] p = line.Split(' ');
            string cmd = p[0].ToUpperInvariant();
            
            try {
                if (cmd == "M" && p.Length >= 3) {
                    int x = int.Parse(p[1], CultureInfo.InvariantCulture);
                    int y = int.Parse(p[2], CultureInfo.InvariantCulture);
                    SetCursorPos(x, y);
                } else if (cmd == "LD") {
                    mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, UIntPtr.Zero);
                } else if (cmd == "LU") {
                    mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, UIntPtr.Zero);
                } else if (cmd == "CLICK" || cmd == "LC") {
                    mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, UIntPtr.Zero);
                    mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, UIntPtr.Zero);
                } else if (cmd == "RD") {
                    mouse_event(MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, UIntPtr.Zero);
                } else if (cmd == "RU") {
                    mouse_event(MOUSEEVENTF_RIGHTUP, 0, 0, 0, UIntPtr.Zero);
                } else if (cmd == "RC") {
                    mouse_event(MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, UIntPtr.Zero);
                    mouse_event(MOUSEEVENTF_RIGHTUP, 0, 0, 0, UIntPtr.Zero);
                } else if (cmd == "W" && p.Length >= 2) {
                    int delta = int.Parse(p[1], CultureInfo.InvariantCulture);
                    mouse_event(MOUSEEVENTF_WHEEL, 0, 0, (uint)delta, UIntPtr.Zero);
                } else if (cmd == "Q") {
                    break;
                }
            } catch {
                // Safeguard against malformed commands
            }
        }
    }
}
