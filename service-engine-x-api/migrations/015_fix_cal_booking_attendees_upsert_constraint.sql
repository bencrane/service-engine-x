-- Ensure ON CONFLICT (cal_booking_uid,email,role) is valid for attendee bulk upserts.
-- The original partial unique index cannot be used as an ON CONFLICT target.

DROP INDEX IF EXISTS uq_cal_booking_attendees_uid_email_role;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'uq_cal_booking_attendees_uid_email_role'
          AND conrelid = 'public.cal_booking_attendees'::regclass
    ) THEN
        ALTER TABLE cal_booking_attendees
            ADD CONSTRAINT uq_cal_booking_attendees_uid_email_role
            UNIQUE (cal_booking_uid, email, role);
    END IF;
END;
$$;
