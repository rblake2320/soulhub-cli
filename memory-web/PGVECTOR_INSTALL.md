# Installing pgvector on Windows (PostgreSQL 16)

## READY TO INSTALL (build already complete)

The pgvector DLL was successfully compiled from source. Run these commands **as Administrator** to install:

```powershell
# Option A: Run the ready-made install script (as Admin)
powershell -File D:\tmp\install_pgvector_admin.ps1

# Option B: Manual install (as Admin)
Copy-Item "D:\tmp\pgvector_src\vector.dll" "C:\Program Files\PostgreSQL\16\lib\vector.dll" -Force
Copy-Item "D:\tmp\pgvector_src\vector.control" "C:\Program Files\PostgreSQL\16\share\extension\vector.control" -Force
Copy-Item "D:\tmp\pgvector_src\sql\vector--0.8.0.sql" "C:\Program Files\PostgreSQL\16\share\extension\vector--0.8.0.sql" -Force
& "C:\Program Files\PostgreSQL\16\bin\psql.exe" -U postgres -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

After installing, run `alembic upgrade head` to update the DB schema, then restart the MemoryWeb server.

---

## Building from source (already done — skip if using files above)

```powershell
# Install vcpkg if not already installed
git clone https://github.com/microsoft/vcpkg.git C:\vcpkg
C:\vcpkg\bootstrap-vcpkg.bat

# Install pgvector (automatically finds PostgreSQL)
C:\vcpkg\vcpkg install pgvector --triplet x64-windows
```

## Option 2: Build from source with Visual Studio Build Tools

1. Install Visual Studio Build Tools 2022 (C++ workload)
2. Download PostgreSQL 16 development headers from EDB
3. Clone pgvector: `git clone https://github.com/pgvector/pgvector.git`
4. Open "x64 Native Tools Command Prompt for VS 2022"
5. Set PostgreSQL path:
   ```
   set PGROOT=C:\Program Files\PostgreSQL\16
   ```
6. Build:
   ```
   nmake /F Makefile.win
   nmake /F Makefile.win install
   ```

## Option 3: Use pre-built EDB StackBuilder
1. Run PostgreSQL StackBuilder (installed with EDB PostgreSQL)
2. Look for "pgvector" extension in the categories
3. Install and restart PostgreSQL service

## Option 4: Use Chocolatey
```powershell
choco install pgvector-postgresql16  # if available
```

## After Installation

```sql
-- Verify in psql:
CREATE EXTENSION IF NOT EXISTS vector;
SELECT * FROM pg_extension WHERE extname = 'vector';
```

## Without pgvector

MemoryWeb runs without pgvector with degraded functionality:
- Tier 1 (structured SQL) and Tier 2 (trigram) search work normally
- Tier 3 (semantic vector search) is disabled
- Memory synthesis and entity extraction work normally
- Embeddings are stored in RAM only (not persisted to DB)

To install later: run `alembic upgrade head` after pgvector is installed.
