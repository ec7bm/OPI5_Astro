# Servidor HTTP Robust (Streaming) para PowerShell
# Uso: .\start_http_server.ps1
# Accesible en: http://LAN_IP:8080/NombreArchivo

$port = 8080
$listener = New-Object System.Net.HttpListener
$listener.Prefixes.Add("http://+:$port/")
$listener.Start()
Write-Host "✅ SERVER STREAMING ON http://localhost:$port/" -ForegroundColor Green
Write-Host "ℹ️  Sirviendo carpeta actual: $PWD" -ForegroundColor Cyan

try {
    while ($listener.IsListening) {
        $ctx = $listener.GetContext()
        $req = $ctx.Request
        $rsp = $ctx.Response
        
        $filename = [Uri]::UnescapeDataString($req.Url.LocalPath.TrimStart('/'))
        $fullpath = Join-Path $PWD.Path $filename
        Write-Host "📥 Request: $filename" -NoNewline
        
        if (Test-Path $fullpath -PathType Leaf) {
            try {
                $fs = [System.IO.File]::OpenRead($fullpath)
                $rsp.ContentLength64 = $fs.Length
                $rsp.SendChunked = $false
                $rsp.ContentType = "application/octet-stream"
                
                $buffer = New-Object byte[] 64KB
                $stream = $rsp.OutputStream
                while (($read = $fs.Read($buffer, 0, $buffer.Length)) -gt 0) {
                    $stream.Write($buffer, 0, $read)
                }
                $fs.Close()
                $stream.Close()
                $rsp.Close()
                Write-Host " -> ✔️ SENT" -ForegroundColor Green
            } catch {
                Write-Host " -> ❌ ERROR: $_" -ForegroundColor Red
                $rsp.StatusCode = 500
                $rsp.Close()
            }
        } else {
            $rsp.StatusCode = 404
            Write-Host " -> ❌ 404" -ForegroundColor Yellow
            $rsp.Close()
        }
    }
} finally { $listener.Stop() }
