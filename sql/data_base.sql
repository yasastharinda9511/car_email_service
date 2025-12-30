CREATE SCHEMA IF NOT EXISTS notifications;

CREATE TABLE IF NOT EXISTS notifications.notifications (
	notification_id UUID PRIMARY KEY,
	notification_type VARCHAR(100) NOT NULL,
	source VARCHAR(100) NOT NULL,
	payload JSONB NOT NULL,
	priority VARCHAR(20) DEFAULT 'normal',
	timestamp TIMESTAMP WITH TIME ZONE,
	reference_id VARCHAR(200),
	metadata JSONB,
	stored_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_notifications_type
	ON notifications.notifications (notification_type);

CREATE INDEX IF NOT EXISTS idx_notifications_source
	ON notifications.notifications (source);

CREATE INDEX IF NOT EXISTS idx_notifications_priority
	ON notifications.notifications (priority);

CREATE INDEX IF NOT EXISTS idx_notifications_stored_at
	ON notifications.notifications (stored_at);