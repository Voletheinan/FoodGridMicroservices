# Smoke test for microservices (PowerShell)
# Waits for services to be healthy, then creates user, restaurant, and an order.

$services = @{
    "user" = "http://localhost:8001/health";
    "restaurant" = "http://localhost:8003/health";
    "order" = "http://localhost:8002/health";
}

foreach ($name in $services.Keys) {
    $url = $services[$name]
    Write-Host "Waiting for $name at $url"
    $ok = $false
    for ($i=0; $i -lt 60; $i++) {
        try {
            $r = Invoke-RestMethod -Method Get -Uri $url -TimeoutSec 2 -UseBasicParsing
            if ($r.status -eq "healthy") { $ok = $true; break }
        } catch {
            Start-Sleep -Seconds 1
        }
    }
    if (-not $ok) {
        Write-Error "$name did not become healthy"
        exit 1
    }
}

Write-Host "All services healthy. Proceeding to create sample data..."

# Create user
$userPayload = '{"username":"alice","email":"alice@example.com"}'
$user = Invoke-RestMethod -Method Post -Uri http://localhost:8001/users -ContentType 'application/json' -Body $userPayload -UseBasicParsing
$user_id = $user.id
Write-Host "Created user id: $user_id"

# Create restaurant
$restPayload = '{"name":"R1","description":"d","address":"a","phone":"p"}'
$rest = Invoke-RestMethod -Method Post -Uri http://localhost:8003/restaurants -ContentType 'application/json' -Body $restPayload -UseBasicParsing
$rest_id = $rest.id
Write-Host "Created restaurant id: $rest_id"

# Create order
$orderObj = @{ user_id = $user_id; restaurant_id = $rest_id; items = @(@{ menu_item_id = "m1"; quantity = 1 }) }
$orderBody = $orderObj | ConvertTo-Json -Depth 5
$order = Invoke-RestMethod -Method Post -Uri http://localhost:8002/orders -ContentType 'application/json' -Body $orderBody -UseBasicParsing
Write-Host "Order created:`n$($order | ConvertTo-Json -Depth 5)"
