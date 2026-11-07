import SwiftUI
import AppKit
import UniformTypeIdentifiers

// MARK: - Utilidades

func programID(npdmPath: String) -> String? {
    guard let d = try? Data(contentsOf: URL(fileURLWithPath: npdmPath)), d.count > 0x78 else { return nil }
    func u32(_ off: Int) -> UInt32 { d.withUnsafeBytes { $0.load(fromByteOffset: off, as: UInt32.self) } }
    func u64(_ off: Int) -> UInt64 { d.withUnsafeBytes { $0.load(fromByteOffset: off, as: UInt64.self) } }
    let off = Int(u32(0x70))
    guard off + 0x18 <= d.count else { return nil }
    let magic = d.subdata(in: off..<(off + 4))
    guard magic == Data("ACI0".utf8) else { return nil }
    return String(format: "%016llX", u64(off + 0x10))
}

struct DumpInfo {
    var titleID: String = ""
    var packages: [String] = []
    var totalBytes: Int64 = 0
    var isValid: Bool = false
}

func analyzeDump(_ url: URL) -> DumpInfo {
    let fm = FileManager.default
    func isDir(_ u: URL) -> Bool {
        var b: ObjCBool = false
        return fm.fileExists(atPath: u.path, isDirectory: &b) && b.boolValue
    }
    var info = DumpInfo()
    let base = url.appendingPathComponent("base")
    let updates = url.appendingPathComponent("updates")

    var npdmCandidates: [String] = [
        base.appendingPathComponent("exefs/main.npdm").path,
        url.appendingPathComponent("exefs/main.npdm").path,
    ]
    var updateNames: [String] = []
    if let items = try? fm.contentsOfDirectory(atPath: updates.path) {
        updateNames = items.filter { Int($0) != nil }.sorted { (Int($0) ?? 0) < (Int($1) ?? 0) }
    }
    for name in updateNames {
        npdmCandidates.append(updates.appendingPathComponent("\(name)/exefs/main.npdm").path)
    }
    for c in npdmCandidates {
        if let pid = programID(npdmPath: c) { info.titleID = pid; break }
    }

    if isDir(base.appendingPathComponent("exefs")) || isDir(base.appendingPathComponent("romfs")) {
        info.packages.append("Base")
    }
    if isDir(url.appendingPathComponent("exefs")) || isDir(url.appendingPathComponent("romfs")) {
        if info.packages.isEmpty { info.packages.append("Base (carpeta plana)") }
    }
    for name in updateNames {
        let u = updates.appendingPathComponent(name)
        if isDir(u.appendingPathComponent("exefs")) || isDir(u.appendingPathComponent("romfs")) {
            info.packages.append("Update \(name)")
        }
    }
    info.isValid = !info.packages.isEmpty

    var total: Int64 = 0
    if let en = fm.enumerator(at: url, includingPropertiesForKeys: [.fileSizeKey, .isRegularFileKey]) {
        for case let f as URL in en {
            if let v = try? f.resourceValues(forKeys: [.fileSizeKey, .isRegularFileKey]),
               v.isRegularFile == true, let s = v.fileSize {
                total += Int64(s)
            }
        }
    }
    info.totalBytes = total
    return info
}

func cleanNameAndVersion(from folderName: String) -> (name: String, version: String) {
    var raw = folderName
    var version = ""
    if let r = folderName.range(of: "_v", options: .backwards) {
        let tail = folderName[r.upperBound...]
        if let first = tail.first, first.isNumber, tail.allSatisfy({ $0.isNumber || $0 == "-" || $0 == "." }) {
            version = tail.replacingOccurrences(of: "-", with: ".")
            raw = String(folderName[..<r.lowerBound])
        }
    }
    var name = raw.replacingOccurrences(of: "_", with: " ").replacingOccurrences(of: "-", with: " ")
    name = name.trimmingCharacters(in: .whitespaces)
    if name.contains(" ") || name == name.lowercased() {
        name = name.capitalized
    }
    return (name, version)
}

// MARK: - Modelo

final class Model: ObservableObject {
    enum Phase { case idle, working, verifying, installing, done, failed }

    @Published var folder: URL?
    @Published var info = DumpInfo()
    @Published var gameName: String = ""
    @Published var displayVersion: String = ""
    @Published var destFolder: URL?
    @Published var verifyAfter: Bool = true
    @Published var phase: Phase = .idle
    @Published var progress: Double = 0
    @Published var statusText: String = "Elige la carpeta de un juego para empezar."
    @Published var log: String = ""
    @Published var toolReady: Bool = false
    @Published var analyzing: Bool = false

    private var proc: Process?
    private let home = FileManager.default.homeDirectoryForCurrentUser
    private var pythonPath: String { home.appendingPathComponent(".venvs/nup/bin/python").path }
    private var nupSrcPath: String { home.appendingPathComponent("nup-tool/tools/nup").path }

    var busy: Bool { phase == .working || phase == .verifying || phase == .installing }

    func checkTool() {
        let fm = FileManager.default
        toolReady = fm.fileExists(atPath: pythonPath) && fm.fileExists(atPath: nupSrcPath)
    }

    var outputURL: URL? {
        guard let folder = folder else { return nil }
        let dir = destFolder ?? folder.deletingLastPathComponent()
        var base = gameName.isEmpty ? folder.lastPathComponent : gameName
        base = base.replacingOccurrences(of: "/", with: "-").replacingOccurrences(of: ":", with: "-")
        if !info.titleID.isEmpty { base += " [\(info.titleID)]" }
        return dir.appendingPathComponent(base + ".nup")
    }

    var outputExists: Bool {
        guard let out = outputURL else { return false }
        return FileManager.default.fileExists(atPath: out.path)
    }

    var canConvert: Bool {
        folder != nil && info.isValid && toolReady && !busy && !outputExists
    }

    func setFolder(_ url: URL) {
        folder = url
        destFolder = nil
        phase = .idle
        progress = 0
        log = ""
        statusText = "Leyendo la carpeta…"
        analyzing = true
        let (n, v) = cleanNameAndVersion(from: url.lastPathComponent)
        gameName = n
        if !v.isEmpty { displayVersion = v }
        DispatchQueue.global(qos: .userInitiated).async {
            let found = analyzeDump(url)
            DispatchQueue.main.async {
                self.analyzing = false
                self.info = found
                if found.isValid {
                    self.statusText = "Carpeta válida. Ya puedes convertir."
                } else {
                    self.statusText = "Esa carpeta no parece un dump de juego (faltan base/, updates/ o exefs/+romfs/)."
                }
            }
        }
    }

    private func appendLog(_ line: String) {
        log += line + "\n"
        if log.count > 12000 { log = String(log.suffix(12000)) }
    }

    private func run(executable: String, args: [String], onLine: @escaping (String) -> Void, onDone: @escaping (Int32) -> Void) {
        let p = Process()
        p.executableURL = URL(fileURLWithPath: executable)
        p.arguments = args
        var env = ProcessInfo.processInfo.environment
        env["PYTHONPATH"] = nupSrcPath
        env["PATH"] = "/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"
        p.environment = env
        let pipe = Pipe()
        p.standardOutput = pipe
        p.standardError = pipe
        var buffer = ""
        let q = DispatchQueue(label: "nup.out")
        pipe.fileHandleForReading.readabilityHandler = { h in
            let data = h.availableData
            if data.isEmpty { return }
            guard let s = String(data: data, encoding: .utf8) else { return }
            q.async {
                buffer += s
                while let nl = buffer.firstIndex(of: "\n") {
                    let line = String(buffer[..<nl])
                    buffer = String(buffer[buffer.index(after: nl)...])
                    DispatchQueue.main.async { onLine(line) }
                }
            }
        }
        p.terminationHandler = { proc in
            pipe.fileHandleForReading.readabilityHandler = nil
            q.async {
                if !buffer.isEmpty {
                    let rest = buffer
                    DispatchQueue.main.async { onLine(rest) }
                }
                DispatchQueue.main.async { onDone(proc.terminationStatus) }
            }
        }
        proc = p
        do {
            try p.run()
        } catch {
            DispatchQueue.main.async { onDone(-1) }
        }
    }

    func cancel() {
        proc?.terminate()
    }

    func installTool() {
        phase = .installing
        log = ""
        statusText = "Instalando la herramienta nup (solo la primera vez)…"
        let script = """
        set -e
        if [ ! -d "$HOME/nup-tool/tools/nup" ]; then
          rm -rf "$HOME/nup-tool" "$HOME/nup-descarga"
          mkdir -p "$HOME/nup-descarga"
          echo "Descargando la herramienta nup…"
          curl -fsSL "https://codeload.github.com/a55uka/nup/zip/refs/heads/meow" -o "$HOME/nup-descarga/nup.zip" || { echo "No se pudo descargar la herramienta. Revisa tu conexión a internet y reintenta."; exit 4; }
          ditto -x -k "$HOME/nup-descarga/nup.zip" "$HOME/nup-descarga"
          mv "$HOME/nup-descarga/nup-meow" "$HOME/nup-tool"
          rm -rf "$HOME/nup-descarga"
          echo "Herramienta descargada"
        fi
        PY=""
        for c in /opt/homebrew/bin/python3.12 /opt/homebrew/bin/python3.13 /opt/homebrew/bin/python3.14 /opt/homebrew/bin/python3.11 /opt/homebrew/bin/python3.10 /Library/Frameworks/Python.framework/Versions/3.14/bin/python3 /Library/Frameworks/Python.framework/Versions/3.13/bin/python3 /Library/Frameworks/Python.framework/Versions/3.12/bin/python3 /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 /usr/local/bin/python3.14 /usr/local/bin/python3.13 /usr/local/bin/python3.12 /usr/local/bin/python3 /opt/homebrew/bin/python3 python3.14 python3.13 python3.12 python3.11 python3.10 python3; do
          if command -v "$c" >/dev/null 2>&1; then PY=$(command -v "$c"); break; fi
        done
        if [ -z "$PY" ]; then
          echo "FALTA_PYTHON"
          echo "— — —"
          echo "Falta Python 3 en este Mac. Es lo único que la app necesita."
          echo "Cómo instalarlo (2 minutos):"
          echo "1. Entra a https://www.python.org/downloads/ y descarga Python para macOS."
          echo "2. Instálalo como cualquier app."
          echo "3. Cierra esta app, vuelve a abrirla y pulsa «Instalar (1 clic)»."
          exit 3
        fi
        echo "Usando Python: $PY"
        "$PY" -m venv "$HOME/.venvs/nup" || { echo "No se pudo crear el entorno de Python. Borra la carpeta ~/.venvs/nup y vuelve a pulsar «Instalar (1 clic)»."; exit 5; }
        "$HOME/.venvs/nup/bin/pip" install -q "zstandard>=0.22" || { echo "No se pudieron instalar las dependencias. Revisa tu conexión a internet y vuelve a intentarlo."; exit 6; }
        echo INSTALACION_OK
        """
        run(executable: "/bin/bash", args: ["-c", script], onLine: { line in
            self.appendLog(line)
        }, onDone: { code in
            if code == 0 {
                self.checkTool()
                self.phase = .idle
                self.statusText = self.toolReady ? "Herramienta lista. Elige la carpeta del juego." : "La instalación terminó pero no encuentro la herramienta."
            } else if self.log.contains("FALTA_PYTHON") {
                self.phase = .failed
                self.statusText = "Falta Python 3: sigue los pasos del registro de abajo."
            } else {
                self.phase = .failed
                self.statusText = "La instalación falló (código \(code)). Revisa el registro de abajo."
            }
        })
    }

    func convert() {
        guard let src = folder, let out = outputURL else { return }
        phase = .working
        progress = 0
        log = ""
        statusText = "Empaquetando…"
        var args = ["-m", "nup.cli", "pack", src.path, out.path]
        if !gameName.isEmpty { args += ["--name", gameName] }
        if !displayVersion.isEmpty { args += ["--display-version", displayVersion] }
        let packRegex = try? NSRegularExpression(pattern: #"pack: (\d+)/(\d+)"#)
        run(executable: pythonPath, args: args, onLine: { line in
            self.appendLog(line)
            if let rx = packRegex,
               let m = rx.firstMatch(in: line, range: NSRange(line.startIndex..., in: line)),
               let r1 = Range(m.range(at: 1), in: line), let r2 = Range(m.range(at: 2), in: line),
               let n = Double(line[r1]), let t = Double(line[r2]), t > 0 {
                self.progress = n / t
                self.statusText = "Empaquetando… \(Int(n)) de \(Int(t)) archivos"
            }
            if line.contains("wrote ") { self.progress = 1 }
        }, onDone: { code in
            if code != 0 {
                self.phase = .failed
                self.statusText = "La conversión falló (código \(code)). Revisa el registro de abajo."
                return
            }
            if self.verifyAfter {
                self.phase = .verifying
                self.statusText = "Verificando el .nup (SHA-256 de cada archivo)…"
                self.run(executable: self.pythonPath, args: ["-m", "nup.cli", "verify", out.path], onLine: { line in
                    self.appendLog(line)
                }, onDone: { vcode in
                    if vcode == 0 {
                        self.phase = .done
                        self.statusText = "✅ Listo y verificado: \(out.lastPathComponent)"
                    } else {
                        self.phase = .failed
                        self.statusText = "El .nup se creó pero la verificación falló. No lo uses; revisa el registro."
                    }
                })
            } else {
                self.phase = .done
                self.statusText = "✅ Listo: \(out.lastPathComponent)"
            }
        })
    }
}

// MARK: - Vista

struct ContentView: View {
    @StateObject private var m = Model()

    var body: some View {
        VStack(alignment: .leading, spacing: 14) {
            HStack(spacing: 12) {
                Text("📦").font(.system(size: 38))
                VStack(alignment: .leading, spacing: 2) {
                    Text("Convertidor NUP").font(.title).bold()
                    Text("Convierte una carpeta de juego de Switch 2 en un archivo .nup")
                        .foregroundStyle(.secondary)
                }
            }

            if !m.toolReady {
                HStack {
                    Text("⚠️ Falta la herramienta de conversión en esta Mac.")
                    Spacer()
                    Button(m.phase == .installing ? "Instalando…" : "Instalar (1 clic)") { m.installTool() }
                        .disabled(m.busy)
                }
                .padding(10)
                .background(Color.yellow.opacity(0.25))
                .cornerRadius(8)
            }

            GroupBox {
                VStack(alignment: .leading, spacing: 8) {
                    if let folder = m.folder {
                        Text("Carpeta:").font(.headline)
                        Text(folder.path).font(.system(.body, design: .monospaced)).lineLimit(2)
                        if m.analyzing {
                            Text("Leyendo…")
                        } else if m.info.isValid {
                            Text("✓ Dump válido  •  \(m.info.packages.joined(separator: "  •  "))")
                            if !m.info.titleID.isEmpty { Text("Título ID: \(m.info.titleID)") }
                            Text("Tamaño: \(ByteCountFormatter.string(fromByteCount: m.info.totalBytes, countStyle: .file))")
                        } else {
                            Text("✗ No se reconoce como dump de juego.").foregroundStyle(.red)
                        }
                        Button("Elegir otra carpeta…") { pickFolder() }
                    } else {
                        VStack(spacing: 8) {
                            Text("1 · Elige la carpeta del juego").font(.headline)
                            Text("La que contiene base/, updates/… o suelta la carpeta aquí.")
                                .foregroundStyle(.secondary)
                            Button("Elegir carpeta…") { pickFolder() }
                                .controlSize(.large)
                        }
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 10)
                    }
                }
                .frame(maxWidth: .infinity, alignment: .leading)
            }

            HStack(spacing: 12) {
                VStack(alignment: .leading, spacing: 4) {
                    Text("Nombre del juego").font(.caption).foregroundStyle(.secondary)
                    TextField("Ej. Pokémon Pokopia", text: $m.gameName).frame(width: 260)
                }
                VStack(alignment: .leading, spacing: 4) {
                    Text("Versión (opcional)").font(.caption).foregroundStyle(.secondary)
                    TextField("Ej. 2.0.1", text: $m.displayVersion).frame(width: 110)
                }
            }

            VStack(alignment: .leading, spacing: 4) {
                Text("Se guardará como:").font(.caption).foregroundStyle(.secondary)
                HStack {
                    Text(m.outputURL?.path ?? "—").font(.system(.body, design: .monospaced)).lineLimit(2)
                    Button("Cambiar carpeta…") { pickDest() }.disabled(m.folder == nil)
                }
                if m.outputExists {
                    Text("⚠️ Ya existe un .nup con ese nombre ahí. Cambia el nombre o la carpeta de destino.")
                        .foregroundStyle(.orange)
                }
            }

            Toggle("Verificar el archivo al terminar (recomendado)", isOn: $m.verifyAfter)

            HStack(spacing: 12) {
                Button {
                    m.convert()
                } label: {
                    Text("2 · Convertir a .nup").font(.headline).padding(.horizontal, 10).padding(.vertical, 4)
                }
                .buttonStyle(.borderedProminent)
                .controlSize(.large)
                .disabled(!m.canConvert)

                if m.busy {
                    Button("Cancelar") { m.cancel() }
                }
                if m.phase == .done, let out = m.outputURL {
                    Button("Mostrar en Finder") {
                        NSWorkspace.shared.activateFileViewerSelecting([out])
                    }
                }
            }

            if m.phase == .working {
                ProgressView(value: m.progress)
            } else if m.phase == .verifying || m.phase == .installing {
                ProgressView()
            }
            Text(m.statusText)

            GroupBox("Registro") {
                ScrollView {
                    Text(m.log.isEmpty ? "—" : m.log)
                        .font(.system(.caption, design: .monospaced))
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .textSelection(.enabled)
                }
                .frame(height: 110)
            }

            HStack {
                Spacer()
                Text("By AbadXDev")
                    .font(.footnote)
                    .foregroundStyle(.secondary)
            }
        }
        .padding(20)
        .frame(width: 640)
        .onAppear {
            m.checkTool()
            for arg in CommandLine.arguments.dropFirst() {
                var isDir: ObjCBool = false
                if FileManager.default.fileExists(atPath: arg, isDirectory: &isDir), isDir.boolValue {
                    m.setFolder(URL(fileURLWithPath: arg))
                    break
                }
            }
        }
        .onDrop(of: [UTType.fileURL], isTargeted: nil) { providers in
            guard let provider = providers.first else { return false }
            provider.loadObject(ofClass: NSURL.self) { obj, _ in
                if let url = obj as? URL {
                    DispatchQueue.main.async { m.setFolder(url) }
                }
            }
            return true
        }
    }

    private func pickFolder() {
        let panel = NSOpenPanel()
        panel.canChooseDirectories = true
        panel.canChooseFiles = false
        panel.allowsMultipleSelection = false
        panel.prompt = "Elegir carpeta"
        if panel.runModal() == .OK, let url = panel.url {
            m.setFolder(url)
        }
    }

    private func pickDest() {
        let panel = NSOpenPanel()
        panel.canChooseDirectories = true
        panel.canChooseFiles = false
        panel.allowsMultipleSelection = false
        panel.prompt = "Guardar aquí"
        if panel.runModal() == .OK, let url = panel.url {
            m.destFolder = url
        }
    }
}

// MARK: - App

@main
struct ConvertidorNUPApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
        }
        .windowResizability(.contentSize)
    }
}
