DELETE FROM duckpass."User" U
WHERE U.verified = FALSE
AND U.created_at <= (CURRENT_TIMESTAMP - INTERVAL '1 day');
