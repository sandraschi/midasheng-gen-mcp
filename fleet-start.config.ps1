# Per-repo fleet start config for midasheng-gen-mcp
# Edit ports/backend target here - start.ps1 is fleet-standard.
@{
    Name         = 'midasheng-gen-mcp'
    BackendPort  = 11159
    FrontendPort = 11160
    HealthPath   = '/api/health'
    WebRoot      = 'webapp'
    Backend = @{
        Kind       = 'module-serve'
        Module     = 'midasheng_gen_mcp'
        ServeArgs  = @('--mode', 'http', '--port', '11159')
        SyncExtras = @('dev')
    }
    Frontend = @{
        Kind           = 'vite-npm'
        PackageManager = 'npm'
        PortEnvVar     = 'VITE_PORT'
        ApiTargetEnv   = 'VITE_API_TARGET'
    }
}
