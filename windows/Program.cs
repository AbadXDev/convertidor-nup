using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Drawing;
using System.Globalization;
using System.IO;
using System.IO.Compression;
using System.Net.Http;
using System.Text;
using System.Text.RegularExpressions;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace ConvertidorNUP
{
    static class Program
    {
        [STAThread]
        static void Main(string[] args)
        {
            Application.EnableVisualStyles();
            Application.SetCompatibleTextRenderingDefault(false);
            var f = new MainForm();
            if (args.Length > 0 && Directory.Exists(args[0]))
                f.LoadFolder(args[0]);
            Application.Run(f);
        }
    }

    // ---------- Utilidades (misma lógica que la versión de macOS) ----------

    static class NupUtil
    {
        public static string ProgramID(string npdmPath)
        {
            try
            {
                byte[] d = File.ReadAllBytes(npdmPath);
                if (d.Length <= 0x78) return null;
                int off = BitConverter.ToInt32(d, 0x70);
                if (off < 0 || off + 0x18 > d.Length) return null;
                string magic = Encoding.ASCII.GetString(d, off, 4);
                if (magic != "ACI0") return null;
                ulong pid = BitConverter.ToUInt64(d, off + 0x10);
                return pid.ToString("X16");
            }
            catch { return null; }
        }

        public static void CleanNameAndVersion(string folderName, out string name, out string version)
        {
            string raw = folderName;
            version = "";
            int idx = folderName.LastIndexOf("_v", StringComparison.Ordinal);
            if (idx >= 0)
            {
                string tail = folderName.Substring(idx + 2);
                bool ok = tail.Length > 0 && char.IsDigit(tail[0]);
                if (ok)
                    foreach (char c in tail)
                        if (!char.IsDigit(c) && c != '-' && c != '.') { ok = false; break; }
                if (ok)
                {
                    version = tail.Replace('-', '.');
                    raw = folderName.Substring(0, idx);
                }
            }
            string n = raw.Replace('_', ' ').Replace('-', ' ').Trim();
            if (n.Contains(" ") || n == n.ToLowerInvariant())
                n = CultureInfo.CurrentCulture.TextInfo.ToTitleCase(n.ToLowerInvariant());
            name = n;
        }
    }

    class DumpInfo
    {
        public string TitleID = "";
        public List<string> Packages = new List<string>();
        public long TotalBytes = 0;
        public bool IsValid { get { return Packages.Count > 0; } }
    }

    static class DumpAnalyzer
    {
        public static DumpInfo Analyze(string root)
        {
            var info = new DumpInfo();
            string baseDir = Path.Combine(root, "base");
            string updatesDir = Path.Combine(root, "updates");

            var updateNames = new List<string>();
            if (Directory.Exists(updatesDir))
            {
                foreach (string d in Directory.GetDirectories(updatesDir))
                {
                    string n = Path.GetFileName(d);
                    int v;
                    if (int.TryParse(n, out v)) updateNames.Add(n);
                }
                updateNames.Sort((a, b) => int.Parse(a).CompareTo(int.Parse(b)));
            }

            var candidates = new List<string>
            {
                Path.Combine(baseDir, "exefs", "main.npdm"),
                Path.Combine(root, "exefs", "main.npdm")
            };
            foreach (string n in updateNames)
                candidates.Add(Path.Combine(updatesDir, n, "exefs", "main.npdm"));
            foreach (string c in candidates)
            {
                string pid = NupUtil.ProgramID(c);
                if (pid != null) { info.TitleID = pid; break; }
            }

            Func<string, bool> hasContent = p =>
                Directory.Exists(Path.Combine(p, "exefs")) || Directory.Exists(Path.Combine(p, "romfs"));
            if (hasContent(baseDir)) info.Packages.Add("Base");
            if (hasContent(root) && info.Packages.Count == 0) info.Packages.Add("Base (carpeta plana)");
            foreach (string n in updateNames)
                if (hasContent(Path.Combine(updatesDir, n)))
                    info.Packages.Add("Update " + n);

            long total = 0;
            try
            {
                foreach (string f in Directory.EnumerateFiles(root, "*", SearchOption.AllDirectories))
                {
                    try { total += new FileInfo(f).Length; } catch { }
                }
            }
            catch { }
            info.TotalBytes = total;
            return info;
        }
    }

    // ---------- Ventana principal ----------

    class MainForm : Form
    {
        static readonly string Home = Environment.GetFolderPath(Environment.SpecialFolder.UserProfile);
        static readonly string RepoDir = Path.Combine(Home, "nup-tool");
        static readonly string VenvDir = Path.Combine(Home, ".venvs", "nup");
        static readonly string VenvPy = Path.Combine(VenvDir, "Scripts", "python.exe");
        static readonly string ModDir = Path.Combine(RepoDir, "tools", "nup");

        Panel banner;
        Label bannerText;
        Button installBtn;
        Label folderLabel, infoLabel, saveLabel, statusLabel;
        TextBox nameBox, versionBox, logBox;
        Button pickBtn, changeDestBtn, convertBtn, cancelBtn, openFolderBtn;
        CheckBox verifyChk;
        ProgressBar progress;

        string folderPath, destDir, outputPath;
        DumpInfo dump;
        Process currentProc;
        bool busy = false, toolReady = false;

        public MainForm()
        {
            Text = "Convertidor NUP";
            Width = 720; Height = 700;
            MinimumSize = new Size(640, 620);
            Font = new Font("Segoe UI", 9.5f);
            StartPosition = FormStartPosition.CenterScreen;
            AllowDrop = true;
            DragEnter += OnDragEnter;
            DragDrop += OnDragDrop;

            var title = new Label { Text = "📦 Convertidor NUP", Font = new Font("Segoe UI", 20, FontStyle.Bold), AutoSize = true, Location = new Point(18, 12) };
            var subtitle = new Label { Text = "Convierte una carpeta de juego de Switch 2 en un archivo .nup", ForeColor = Color.Gray, AutoSize = true, Location = new Point(20, 52) };
            Controls.Add(title); Controls.Add(subtitle);

            banner = new Panel { BackColor = Color.FromArgb(255, 248, 220), Location = new Point(20, 78), Size = new Size(664, 40), Anchor = AnchorStyles.Top | AnchorStyles.Left | AnchorStyles.Right, Visible = false };
            bannerText = new Label { Text = "La herramienta de empaquetado no está instalada todavía.", AutoSize = true, Location = new Point(10, 11) };
            installBtn = new Button { Text = "Instalar", Location = new Point(560, 7), Size = new Size(92, 26), Anchor = AnchorStyles.Top | AnchorStyles.Right };
            installBtn.Click += async (s, e) => await InstallTool();
            banner.Controls.Add(bannerText); banner.Controls.Add(installBtn);
            Controls.Add(banner);

            var g1 = new GroupBox { Text = "1 · Elige la carpeta del juego", Location = new Point(20, 126), Size = new Size(664, 118), Anchor = AnchorStyles.Top | AnchorStyles.Left | AnchorStyles.Right };
            pickBtn = new Button { Text = "Elegir carpeta…", Location = new Point(16, 26), Size = new Size(150, 30) };
            pickBtn.Click += (s, e) => PickFolder();
            folderLabel = new Label { Text = "La que contiene base/, updates/… o arrastra la carpeta a esta ventana.", ForeColor = Color.Gray, AutoSize = false, Location = new Point(178, 26), Size = new Size(470, 42) };
            infoLabel = new Label { Text = "", AutoSize = false, Location = new Point(16, 64), Size = new Size(630, 46) };
            g1.Controls.Add(pickBtn); g1.Controls.Add(folderLabel); g1.Controls.Add(infoLabel);
            Controls.Add(g1);

            var nameLbl = new Label { Text = "Nombre del juego", AutoSize = true, Location = new Point(20, 256) };
            nameBox = new TextBox { Location = new Point(20, 278), Size = new Size(400, 26), PlaceholderText = "Ej. Pokémon Pokopia" };
            nameBox.TextChanged += (s, e) => UpdateOutput();
            var verLbl = new Label { Text = "Versión (opcional)", AutoSize = true, Location = new Point(440, 256) };
            versionBox = new TextBox { Location = new Point(440, 278), Size = new Size(180, 26), PlaceholderText = "Ej. 2.0.1" };
            Controls.Add(nameLbl); Controls.Add(nameBox); Controls.Add(verLbl); Controls.Add(versionBox);

            saveLabel = new Label { Text = "Se guardará como: —", AutoSize = false, Location = new Point(20, 316), Size = new Size(480, 22) };
            changeDestBtn = new Button { Text = "Cambiar carpeta…", Location = new Point(520, 312), Size = new Size(164, 28), Enabled = false };
            changeDestBtn.Click += (s, e) => ChangeDest();
            Controls.Add(saveLabel); Controls.Add(changeDestBtn);

            verifyChk = new CheckBox { Text = "Verificar el archivo al terminar (recomendado)", Checked = true, AutoSize = true, Location = new Point(20, 344) };
            Controls.Add(verifyChk);

            convertBtn = new Button { Text = "2 · Convertir a .nup", Font = new Font("Segoe UI", 11, FontStyle.Bold), Location = new Point(20, 376), Size = new Size(240, 40), Enabled = false, BackColor = Color.FromArgb(0, 120, 215), ForeColor = Color.White };
            convertBtn.Click += async (s, e) => await Convert();
            cancelBtn = new Button { Text = "Cancelar", Location = new Point(272, 376), Size = new Size(110, 40), Visible = false };
            cancelBtn.Click += (s, e) => { try { currentProc?.Kill(true); } catch { } };
            openFolderBtn = new Button { Text = "Abrir carpeta", Location = new Point(272, 376), Size = new Size(130, 40), Visible = false };
            openFolderBtn.Click += (s, e) => { if (outputPath != null) Process.Start("explorer.exe", "/select,\"" + outputPath + "\""); };
            Controls.Add(convertBtn); Controls.Add(cancelBtn); Controls.Add(openFolderBtn);

            progress = new ProgressBar { Location = new Point(20, 426), Size = new Size(664, 18), Anchor = AnchorStyles.Top | AnchorStyles.Left | AnchorStyles.Right, Style = ProgressBarStyle.Continuous };
            Controls.Add(progress);
            statusLabel = new Label { Text = "Elige la carpeta de un juego para empezar.", AutoSize = false, Location = new Point(20, 450), Size = new Size(664, 24) };
            Controls.Add(statusLabel);

            var g2 = new GroupBox { Text = "Registro", Location = new Point(20, 480), Size = new Size(664, 130), Anchor = AnchorStyles.Top | AnchorStyles.Bottom | AnchorStyles.Left | AnchorStyles.Right };
            logBox = new TextBox { Multiline = true, ReadOnly = true, ScrollBars = ScrollBars.Vertical, Font = new Font("Consolas", 9), Dock = DockStyle.Fill, Text = "—" };
            g2.Controls.Add(logBox);
            Controls.Add(g2);

            var credit = new Label { Text = "By AbadXDev", ForeColor = Color.Gray, AutoSize = true, Anchor = AnchorStyles.Bottom | AnchorStyles.Right };
            credit.Location = new Point(600, 640);
            Controls.Add(credit);
            Resize += (s, e) => credit.Location = new Point(ClientSize.Width - 92, ClientSize.Height - 24);

            Load += (s, e) =>
            {
                credit.Location = new Point(ClientSize.Width - 92, ClientSize.Height - 24);
                CheckTool();
            };
        }

        // ---------- Herramienta nup ----------

        void CheckTool()
        {
            toolReady = File.Exists(VenvPy) && Directory.Exists(ModDir);
            banner.Visible = !toolReady;
        }

        void Log(string line)
        {
            if (logBox.Text == "—") logBox.Text = "";
            logBox.AppendText(line + Environment.NewLine);
        }

        async Task<int> RunCmd(string file, string args, string workDir, Action<string> onLine, string extraPath = null)
        {
            var psi = new ProcessStartInfo
            {
                FileName = file,
                Arguments = args,
                WorkingDirectory = workDir ?? Home,
                UseShellExecute = false,
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                CreateNoWindow = true,
                StandardOutputEncoding = Encoding.UTF8,
                StandardErrorEncoding = Encoding.UTF8
            };
            if (extraPath != null) psi.EnvironmentVariables["PYTHONPATH"] = extraPath;
            var p = new Process { StartInfo = psi, EnableRaisingEvents = true };
            currentProc = p;
            p.OutputDataReceived += (s, e) => { if (e.Data != null) BeginInvoke((Action)(() => onLine(e.Data))); };
            p.ErrorDataReceived += (s, e) => { if (e.Data != null) BeginInvoke((Action)(() => onLine(e.Data))); };
            p.Start();
            p.BeginOutputReadLine(); p.BeginErrorReadLine();
            await Task.Run(() => p.WaitForExit());
            currentProc = null;
            return p.ExitCode;
        }

        static string Q(string s) { return "\"" + s.Replace("\"", "\\\"") + "\""; }

        class PythonMissingException : Exception { public PythonMissingException() : base("Falta Python 3") { } }

        async Task<bool> PythonOk(string file, string args)
        {
            try { return await RunCmd(file, args, Home, _ => { }) == 0; }
            catch { return false; }
        }

        async Task DownloadTool()
        {
            string zipPath = Path.Combine(Home, "nup-descarga.zip");
            string tmpDir = Path.Combine(Home, "nup-descarga");
            Log("Descargando la herramienta nup\u2026");
            try
            {
                using (var http = new HttpClient())
                {
                    http.DefaultRequestHeaders.UserAgent.ParseAdd("ConvertidorNUP");
                    var data = await http.GetByteArrayAsync("https://codeload.github.com/a55uka/nup/zip/refs/heads/meow");
                    File.WriteAllBytes(zipPath, data);
                }
            }
            catch { throw new Exception("No se pudo descargar la herramienta. Revisa tu conexi\u00f3n a internet y reintenta."); }
            if (Directory.Exists(tmpDir)) Directory.Delete(tmpDir, true);
            ZipFile.ExtractToDirectory(zipPath, tmpDir);
            string inner = Path.Combine(tmpDir, "nup-meow");
            if (!Directory.Exists(inner)) throw new Exception("La descarga no tiene el formato esperado. Reintenta.");
            if (Directory.Exists(RepoDir)) Directory.Delete(RepoDir, true);
            Directory.Move(inner, RepoDir);
            Directory.Delete(tmpDir, true);
            File.Delete(zipPath);
            Log("Herramienta descargada.");
        }

        void ShowPythonHelp()
        {
            Log("\u2014 \u2014 \u2014");
            Log("FALTA PYTHON 3 en este equipo. Es lo \u00fanico que la app necesita.");
            Log("C\u00f3mo instalarlo (2 minutos):");
            Log("1. Acepta el aviso siguiente para abrir la p\u00e1gina de descarga de Python.");
            Log("2. Al instalarlo, MARCA la casilla \u00abAdd python.exe to PATH\u00bb.");
            Log("3. Cuando termine, cierra esta app, vuelve a abrirla y pulsa \u00abInstalar\u00bb.");
            var r = MessageBox.Show(
                "Para terminar la instalaci\u00f3n falta Python 3.\n\n" +
                "1. Descarga Python desde python.org.\n" +
                "2. Al instalarlo, marca la casilla \u00abAdd python.exe to PATH\u00bb.\n" +
                "3. Cierra esta app, vuelve a abrirla y pulsa \u00abInstalar\u00bb.\n\n" +
                "\u00bfQuieres abrir ahora la p\u00e1gina de descarga de Python?",
                "Falta Python 3", MessageBoxButtons.YesNo, MessageBoxIcon.Information);
            if (r == DialogResult.Yes)
                Process.Start(new ProcessStartInfo("https://www.python.org/downloads/") { UseShellExecute = true });
        }

        async Task InstallTool()
        {
            if (busy) return;
            busy = true; installBtn.Enabled = false;
            statusLabel.Text = "Instalando la herramienta\u2026 (solo la primera vez)";
            try
            {
                if (!Directory.Exists(ModDir))
                {
                    if (Directory.Exists(RepoDir)) Directory.Delete(RepoDir, true);
                    await DownloadTool();
                }
                if (!File.Exists(VenvPy))
                {
                    Log("Creando el entorno de Python\u2026");
                    Directory.CreateDirectory(Path.GetDirectoryName(VenvDir));
                    int rc = -1;
                    if (await PythonOk("py", "-3 --version")) rc = await RunCmd("py", "-3 -m venv " + Q(VenvDir), Home, Log);
                    else if (await PythonOk("python", "--version")) rc = await RunCmd("python", "-m venv " + Q(VenvDir), Home, Log);
                    if (rc != 0) throw new PythonMissingException();
                }
                Log("Instalando dependencias\u2026");
                int rc2 = await RunCmd(VenvPy, "-m pip install --disable-pip-version-check zstandard", Home, Log);
                if (rc2 != 0) throw new Exception("No se pudieron instalar las dependencias. Revisa tu conexi\u00f3n a internet y reintenta.");
                Log("Herramienta instalada \u2713");
                statusLabel.Text = "Herramienta lista. Ya puedes convertir.";
            }
            catch (PythonMissingException)
            {
                statusLabel.Text = "Falta Python 3: sigue los pasos del registro de abajo.";
                ShowPythonHelp();
            }
            catch (Exception ex)
            {
                statusLabel.Text = "No se pudo instalar: " + ex.Message;
                Log("ERROR: " + ex.Message);
            }
            busy = false; installBtn.Enabled = true;
            CheckTool();
            UpdateConvertEnabled();
        }

        // ---------- Carpeta / análisis ----------

        void PickFolder()
        {
            using (var d = new FolderBrowserDialog { Description = "Elige la carpeta del juego (la que contiene base/, updates/…)" })
                if (d.ShowDialog() == DialogResult.OK) LoadFolder(d.SelectedPath);
        }

        void OnDragEnter(object s, DragEventArgs e)
        {
            if (e.Data.GetDataPresent(DataFormats.FileDrop)) e.Effect = DragDropEffects.Copy;
        }

        void OnDragDrop(object s, DragEventArgs e)
        {
            var files = (string[])e.Data.GetData(DataFormats.FileDrop);
            if (files.Length > 0 && Directory.Exists(files[0])) LoadFolder(files[0]);
        }

        public async void LoadFolder(string path)
        {
            folderPath = path;
            destDir = Directory.GetParent(path)?.FullName ?? path;
            folderLabel.Text = path;
            folderLabel.ForeColor = Color.Black;
            infoLabel.Text = "Analizando…";
            statusLabel.Text = "Analizando la carpeta…";
            convertBtn.Enabled = false;
            dump = await Task.Run(() => DumpAnalyzer.Analyze(path));
            if (dump.IsValid)
            {
                string size = dump.TotalBytes >= (1L << 30)
                    ? (dump.TotalBytes / 1073741824.0).ToString("F2") + " GB"
                    : (dump.TotalBytes / 1048576.0).ToString("F0") + " MB";
                infoLabel.Text = "✓ Dump válido • " + string.Join(" • ", dump.Packages) +
                    (dump.TitleID != "" ? "\r\nTítulo ID: " + dump.TitleID : "") +
                    "\r\nTamaño: " + size;
                string n, v;
                NupUtil.CleanNameAndVersion(Path.GetFileName(path), out n, out v);
                if (nameBox.Text.Trim() == "") nameBox.Text = n;
                if (versionBox.Text.Trim() == "" && v != "") versionBox.Text = v;
                statusLabel.Text = "Carpeta válida. Ya puedes convertir.";
            }
            else
            {
                infoLabel.Text = "⚠ No parece un dump válido: falta base/ o updates/ con exefs/ o romfs/.";
                statusLabel.Text = "Esa carpeta no parece un dump de juego.";
            }
            changeDestBtn.Enabled = dump.IsValid;
            UpdateOutput();
        }

        void ChangeDest()
        {
            using (var d = new FolderBrowserDialog { Description = "¿Dónde quieres guardar el .nup?" })
            {
                if (destDir != null) d.SelectedPath = destDir;
                if (d.ShowDialog() == DialogResult.OK) { destDir = d.SelectedPath; UpdateOutput(); }
            }
        }

        string SanitizedName()
        {
            string n = nameBox.Text.Trim();
            foreach (char c in Path.GetInvalidFileNameChars()) n = n.Replace(c.ToString(), "");
            return n.Trim();
        }

        void UpdateOutput()
        {
            if (folderPath == null || dump == null || !dump.IsValid || SanitizedName() == "" || dump.TitleID == "")
            {
                saveLabel.Text = "Se guardará como: —";
                convertBtn.Enabled = false;
                return;
            }
            outputPath = Path.Combine(destDir, SanitizedName() + " [" + dump.TitleID + "].nup");
            if (File.Exists(outputPath))
            {
                saveLabel.Text = "⚠ Ya existe un archivo con ese nombre: " + outputPath;
                saveLabel.ForeColor = Color.DarkOrange;
                convertBtn.Enabled = false;
            }
            else
            {
                saveLabel.Text = "Se guardará como: " + outputPath;
                saveLabel.ForeColor = Color.Black;
                UpdateConvertEnabled();
            }
        }

        void UpdateConvertEnabled()
        {
            convertBtn.Enabled = !busy && toolReady && dump != null && dump.IsValid &&
                                 outputPath != null && !File.Exists(outputPath) && SanitizedName() != "";
        }

        // ---------- Conversión ----------

        async Task Convert()
        {
            if (busy || outputPath == null) return;
            busy = true;
            convertBtn.Enabled = false; cancelBtn.Visible = true; openFolderBtn.Visible = false;
            pickBtn.Enabled = false;
            progress.Value = 0;
            statusLabel.Text = "Convirtiendo…";
            string name = SanitizedName();
            string ver = versionBox.Text.Trim();
            string args = "-m nup.cli pack " + Q(folderPath) + " " + Q(outputPath) + " --name " + Q(name);
            if (ver != "") args += " --display-version " + Q(ver);
            Log("Convirtiendo " + folderPath);
            var packRe = new Regex(@"pack:\s*(\d+)\s*/\s*(\d+)");
            int rc = await RunCmd(VenvPy, args, folderPath, line =>
            {
                Log(line);
                var m = packRe.Match(line);
                if (m.Success)
                {
                    int cur = int.Parse(m.Groups[1].Value), tot = int.Parse(m.Groups[2].Value);
                    if (tot > 0) progress.Value = Math.Min(100, cur * 100 / tot);
                }
            }, ModDir);
            if (rc != 0 || !File.Exists(outputPath))
            {
                statusLabel.Text = "La conversión falló. Revisa el registro.";
                Log("ERROR: la herramienta terminó con código " + rc);
                busy = false; cancelBtn.Visible = false; pickBtn.Enabled = true;
                UpdateConvertEnabled();
                return;
            }
            progress.Value = 100;
            if (verifyChk.Checked)
            {
                statusLabel.Text = "Verificando el archivo…";
                int rv = await RunCmd(VenvPy, "-m nup.cli verify " + Q(outputPath), folderPath, Log, ModDir);
                if (rv != 0)
                {
                    statusLabel.Text = "El archivo se creó, pero la verificación falló.";
                    busy = false; cancelBtn.Visible = false; pickBtn.Enabled = true;
                    return;
                }
            }
            var fi = new FileInfo(outputPath);
            statusLabel.Text = "✅ ¡Listo! " + Path.GetFileName(outputPath) + " (" + (fi.Length / 1048576.0).ToString("F1") + " MB)";
            Log("LISTO: " + outputPath);
            openFolderBtn.Visible = true;
            busy = false; cancelBtn.Visible = false; pickBtn.Enabled = true;
            UpdateOutput();
        }
    }
}
