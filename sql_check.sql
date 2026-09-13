SELECT pg_get_triggerdef(oid) FROM pg_trigger WHERE tgname LIKE '%dividend%';
SELECT pg_get_triggerdef(oid) FROM pg_trigger WHERE tgname LIKE '%loan%';
