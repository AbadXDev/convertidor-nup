import AppKit

// Genera icon-1024.png: cuadrado redondeado azul, una caja y el texto NUP.
let size: CGFloat = 1024
let outPath = CommandLine.arguments.count > 1 ? CommandLine.arguments[1] : "icon-1024.png"

let image = NSImage(size: NSSize(width: size, height: size))
image.lockFocus()

let rect = NSRect(x: 52, y: 52, width: size - 104, height: size - 104)
let path = NSBezierPath(roundedRect: rect, xRadius: 200, yRadius: 200)
let gradient = NSGradient(colors: [NSColor(calibratedRed: 0.10, green: 0.35, blue: 0.85, alpha: 1),
                                   NSColor(calibratedRed: 0.45, green: 0.20, blue: 0.85, alpha: 1)])
gradient?.draw(in: path, angle: -45)

let emoji = "📦" as NSString
let emojiAttrs: [NSAttributedString.Key: Any] = [.font: NSFont.systemFont(ofSize: 430)]
let emojiSize = emoji.size(withAttributes: emojiAttrs)
emoji.draw(at: NSPoint(x: (size - emojiSize.width) / 2, y: 350), withAttributes: emojiAttrs)

let label = "NUP" as NSString
let labelAttrs: [NSAttributedString.Key: Any] = [
    .font: NSFont.systemFont(ofSize: 210, weight: .heavy),
    .foregroundColor: NSColor.white,
]
let labelSize = label.size(withAttributes: labelAttrs)
label.draw(at: NSPoint(x: (size - labelSize.width) / 2, y: 110), withAttributes: labelAttrs)

image.unlockFocus()

guard let tiff = image.tiffRepresentation,
      let rep = NSBitmapImageRep(data: tiff),
      let png = rep.representation(using: .png, properties: [:]) else {
    print("ERROR: no se pudo generar el icono")
    exit(1)
}
try! png.write(to: URL(fileURLWithPath: outPath))
print("icono OK: \(outPath)")
