---
description: Never modify or remove the platform admin access for crscentral.rm@gmail.com
---

# Admin Access Protection Rule

**CRITICAL:** Under NO circumstances should you ever modify, overwrite, or delete the `is_platform_admin()` SQL function or any Row Level Security (RLS) policies that grant access to `crscentral.rm@gmail.com`.

The user `crscentral.rm@gmail.com` is the root Platform Admin for the entire application. Modifying their access can result in a catastrophic lockout.

If you are asked to write SQL migrations that involve deleting or updating companies, ensure you do not inadvertently drop or replace existing policies related to platform admins.
