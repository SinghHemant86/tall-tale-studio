# Tall-Tale Studio - connect your YouTube channel (Windows, no Python needed)
#
# 1. Put this file in the same folder as the client_secret JSON downloaded from Google Cloud
# 2. Right-click this file > "Run with PowerShell"
#    (or in a terminal:  powershell -ExecutionPolicy Bypass -File get_youtube_token.ps1)
# 3. Sign in with the Google account that owns the Tall-Tale channel and pick the channel.
# 4. Copy the three printed values into GitHub > repo Settings > Secrets and variables > Actions.

$ErrorActionPreference = 'Stop'
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
# Uses client_secret.json, or Google's long "client_secret_....json" name, whichever is newest.
$secretFile = Get-ChildItem -Path $here -Filter 'client_secret*.json' | Sort-Object LastWriteTime -Descending | Select-Object -First 1
if (-not $secretFile) {
    Write-Host "No client_secret*.json found next to this script ($here)." -ForegroundColor Red
    Read-Host "Press Enter to close"; exit 1
}
$secretPath = $secretFile.FullName
Write-Host "Using $($secretFile.Name)"
$info = (Get-Content $secretPath -Raw | ConvertFrom-Json).installed
if (-not $info) {
    Write-Host "This JSON is not a 'Desktop app' client. Create a Desktop app client in Google Cloud." -ForegroundColor Red
    Read-Host "Press Enter to close"; exit 1
}

$port = 8765
$redirect = "http://127.0.0.1:$port"
$scopes = "https://www.googleapis.com/auth/youtube.upload https://www.googleapis.com/auth/youtube.readonly"
$state = [guid]::NewGuid().ToString('N')
$authUrl = "https://accounts.google.com/o/oauth2/v2/auth" +
    "?client_id=" + [uri]::EscapeDataString($info.client_id) +
    "&redirect_uri=" + [uri]::EscapeDataString($redirect) +
    "&response_type=code" +
    "&scope=" + [uri]::EscapeDataString($scopes) +
    "&access_type=offline&prompt=" + [uri]::EscapeDataString("select_account consent") +
    "&state=" + $state

# Small local listener that catches Google's redirect after you approve.
$listener = [System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Loopback, $port)
$listener.Start()
Start-Process $authUrl
Write-Host ""
Write-Host "A browser window has opened." -ForegroundColor Yellow
Write-Host " - On 'Choose an account', pick the Tall-Tale channel itself (it is listed as its own entry"
Write-Host "   under simhamanthan@gmail.com), NOT the plain Gmail account"
Write-Host " - On 'Google hasn't verified this app': click Advanced > Go to Tall-Tale-Studio (unsafe)"
Write-Host " - Tick both permissions and click Continue"
Write-Host ""
Write-Host "Waiting for you to finish in the browser..."

$params = $null
while (-not $params) {
    $client = $listener.AcceptTcpClient()
    $stream = $client.GetStream()
    $reader = New-Object System.IO.StreamReader($stream)
    $line = $reader.ReadLine()
    $ok = $line -and ($line -match '[?&](code|error)=')
    if ($ok) {
        $body = "<html><body style='font-family:Georgia,serif;background:#111626;color:#deb96e;text-align:center;padding-top:90px'><h2>Tall-Tale Studio</h2><p style='color:#e8e2d4'>Done. Close this tab and go back to the PowerShell window.</p></body></html>"
        $status = "200 OK"
    } else {
        $body = ""; $status = "404 Not Found"
    }
    $resp = "HTTP/1.1 $status`r`nContent-Type: text/html; charset=utf-8`r`nContent-Length: " +
            [Text.Encoding]::UTF8.GetByteCount($body) + "`r`nConnection: close`r`n`r`n" + $body
    $bytes = [Text.Encoding]::UTF8.GetBytes($resp)
    try { $stream.Write($bytes, 0, $bytes.Length); $stream.Flush() } catch {}
    $client.Close()
    if ($ok) {
        $query = $line.Split(' ')[1]
        $query = $query.Substring($query.IndexOf('?') + 1)
        $params = @{}
        foreach ($pair in $query.Split('&')) {
            $kv = $pair.Split('=', 2)
            $params[$kv[0]] = [uri]::UnescapeDataString($kv[1])
        }
    }
}
$listener.Stop()

if ($params['error']) {
    Write-Host "Google returned an error: $($params['error'])" -ForegroundColor Red
    Read-Host "Press Enter to close"; exit 1
}
if ($params['state'] -ne $state) {
    Write-Host "Security check failed (state mismatch). Run the script again." -ForegroundColor Red
    Read-Host "Press Enter to close"; exit 1
}

$token = Invoke-RestMethod -Method Post -Uri "https://oauth2.googleapis.com/token" -Body @{
    code          = $params['code']
    client_id     = $info.client_id
    client_secret = $info.client_secret
    redirect_uri  = $redirect
    grant_type    = "authorization_code"
}
if (-not $token.refresh_token) {
    Write-Host "No refresh token came back. Remove the app at https://myaccount.google.com/permissions and run again." -ForegroundColor Red
    Read-Host "Press Enter to close"; exit 1
}

$expected = "UC1n91AJFKbBX_UxWMDDKtRQ"   # Tall-Tale (@TallTale-4u)
$ch = Invoke-RestMethod -Uri "https://www.googleapis.com/youtube/v3/channels?part=snippet&mine=true" `
      -Headers @{ Authorization = "Bearer $($token.access_token)" }
Write-Host ""
if ($ch.items -and $ch.items[0].id -ne $expected) {
    Write-Host ("Connected to the WRONG channel: " + $ch.items[0].snippet.title + " (" + $ch.items[0].id + ")") -ForegroundColor Red
    Write-Host "Run the script again and pick the Tall-Tale entry on the 'Choose an account' screen." -ForegroundColor Yellow
    Write-Host "Nothing to save this time."
    Read-Host "Press Enter to close"; exit 1
} elseif ($ch.items) {
    Write-Host ("Connected channel: " + $ch.items[0].snippet.title + "  (" + $ch.items[0].id + ")  - correct, this is Tall-Tale") -ForegroundColor Green
} else {
    Write-Host "Signed in, but this account has no YouTube channel. Run again and pick the Tall-Tale channel." -ForegroundColor Red
}

Write-Host ""
Write-Host "Add these three as GitHub Actions secrets (repo Settings > Secrets and variables > Actions):" -ForegroundColor Cyan
Write-Host ""
Write-Host "YT_CLIENT_ID      = $($info.client_id)"
Write-Host "YT_CLIENT_SECRET  = $($info.client_secret)"
Write-Host "YT_REFRESH_TOKEN  = $($token.refresh_token)"
Write-Host ""
Write-Host "To avoid copy mistakes, each value can go straight to the clipboard:" -ForegroundColor Cyan
foreach ($pair in @(@("YT_CLIENT_ID", $info.client_id), @("YT_CLIENT_SECRET", $info.client_secret), @("YT_REFRESH_TOKEN", $token.refresh_token))) {
    Read-Host ("Press Enter to copy " + $pair[0] + ", then paste it into that GitHub secret")
    Set-Clipboard -Value ($pair[1].Trim())
    Write-Host ("  " + $pair[0] + " copied.") -ForegroundColor Green
}
Write-Host ""
Write-Host "Keep this window open until all three are saved in GitHub, then close it."
Write-Host "Never paste these values into chat or commit them to the repo."
Write-Host "After saving them, delete the client_secret JSON files from this folder."
Read-Host "Press Enter to close"
