# 🔁 Automatyczne testy proxy_router lokalnie

function Send-ProxyRequest {
    param (
        [string]$Action,
        [hashtable]$Params
    )

    $uri = "http://localhost:7071/api/proxy_router"
    $headers = @{ "Content-Type" = "application/json" }

    $body = @{
        action = $Action
        params = $Params
    } | ConvertTo-Json -Depth 10

    Write-Host "`n▶️  ACTION: $Action"
    Write-Host "Payload: $body"

    try {
        $response = Invoke-RestMethod -Uri $uri -Method Post -Headers $headers -Body $body
        Write-Host "`n✅ Response:`n$response`n"
    } catch {
        Write-Host "`n❌ Error:`n$($_.Exception.Message)`n"
    }
}

# 🧪 TEST 1 — get_current_time
Send-ProxyRequest -Action "get_current_time" -Params @{}

# 🧪 TEST 2 — list_blobs
Send-ProxyRequest -Action "list_blobs" -Params @{}

# 🧪 TEST 3 — read_blob_file
Send-ProxyRequest -Action "read_blob_file" -Params @{ file_name = "example.json" }

# 🧪 TEST 4 — upload_data_or_file
Send-ProxyRequest -Action "upload_data_or_file" -Params @{
    target_blob_name = "example.json"
    file_content = '{ "from": "PowerShell", "time": "' + (Get-Date) + '" }'
}

# 🧪 TEST 5 — remove_data_entry (przykład z brakującym parametrem)
Send-ProxyRequest -Action "remove_data_entry" -Params @{
    target_blob_name = "example.json"
    key_to_find = "id"
    # value_to_find = "123"  # ← Zakomentowany, żeby pokazać walidację
}
