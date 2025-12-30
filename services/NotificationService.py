import json
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from fastapi import HTTPException

from db.DataBase import Database


class NotificationService:
    """
    Service for storing notifications in PostgreSQL database
    """

    def __init__(self, data_base: Database):
        """
        Initialize the notification service with database connection

        Args:
            data_base: Database instance for storing notifications
        """
        self.data_base = data_base

    def store_notification(self, notification_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Store a notification in the database

        Args:
            notification_data: Dictionary containing notification fields

        Returns:
            Dictionary with storage confirmation details

        Raises:
            HTTPException: If storage operation fails
        """
        try:
            # Generate unique notification ID
            notification_id = str(uuid.uuid4())

            # Auto-generate timestamp if not provided
            timestamp = notification_data.get("timestamp")
            if not timestamp:
                timestamp = datetime.now(timezone.utc).isoformat()

            # Prepare data for insertion
            notification_type = notification_data["notification_type"]
            source = notification_data["source"]
            payload = json.dumps(notification_data["payload"])  # Convert dict to JSON string
            priority = notification_data.get("priority", "normal")
            reference_id = notification_data.get("reference_id")
            metadata = json.dumps(notification_data.get("metadata")) if notification_data.get("metadata") else None
            stored_at = datetime.now(timezone.utc).isoformat()

            # Insert into database
            insert_query = """
            INSERT INTO notifications (
                notification_id, notification_type, source, payload,
                priority, timestamp, reference_id, metadata, stored_at
            ) VALUES (%s, %s, %s, %s::jsonb, %s, %s, %s, %s::jsonb, %s)
            """

            self.data_base.execute_update(
                insert_query,
                (notification_id, notification_type, source, payload,
                 priority, timestamp, reference_id, metadata, stored_at)
            )

            return {
                "notification_id": notification_id,
                "notification_type": notification_type,
                "source": source,
                "stored_at": stored_at
            }

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error storing notification: {str(e)}"
            )

    def get_notification_by_id(self, notification_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a notification by ID

        Args:
            notification_id: UUID of the notification

        Returns:
            Notification data as dictionary or None if not found
        """
        try:
            query = """
            SELECT notification_id, notification_type, source, payload,
                   priority, timestamp, reference_id, metadata, stored_at
            FROM notifications
            WHERE notification_id = %s
            """

            results = self.data_base.execute_query(query, (notification_id,))

            if results:
                notification = results[0]
                # Parse JSON fields
                if notification.get('payload'):
                    notification['payload'] = notification['payload']  # Already parsed by psycopg2 for JSONB
                if notification.get('metadata'):
                    notification['metadata'] = notification['metadata']
                return notification
            return None

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error retrieving notification: {str(e)}"
            )

    def get_notifications(
        self,
        notification_type: Optional[str] = None,
        source: Optional[str] = None,
        priority: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Retrieve notifications with optional filters

        Args:
            notification_type: Filter by notification type
            source: Filter by source
            priority: Filter by priority
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            List of notifications
        """
        try:
            # Build dynamic query
            where_clauses = []
            params = []

            if notification_type:
                where_clauses.append("notification_type = %s")
                params.append(notification_type)

            if source:
                where_clauses.append("source = %s")
                params.append(source)

            if priority:
                where_clauses.append("priority = %s")
                params.append(priority)

            where_clause = " AND ".join(where_clauses) if where_clauses else "1=1"

            query = f"""
            SELECT notification_id, notification_type, source, payload,
                   priority, timestamp, reference_id, metadata, stored_at
            FROM notifications
            WHERE {where_clause}
            ORDER BY stored_at DESC
            LIMIT %s OFFSET %s
            """

            params.extend([limit, offset])

            results = self.data_base.execute_query(query, tuple(params))

            # Parse JSON fields (already done by psycopg2 for JSONB)
            return results

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error retrieving notifications: {str(e)}"
            )

    def get_notification_count(
        self,
        notification_type: Optional[str] = None,
        source: Optional[str] = None,
        priority: Optional[str] = None
    ) -> int:
        """
        Get count of notifications with optional filters

        Args:
            notification_type: Filter by notification type
            source: Filter by source
            priority: Filter by priority

        Returns:
            Number of notifications matching filters
        """
        try:
            where_clauses = []
            params = []

            if notification_type:
                where_clauses.append("notification_type = %s")
                params.append(notification_type)

            if source:
                where_clauses.append("source = %s")
                params.append(source)

            if priority:
                where_clauses.append("priority = %s")
                params.append(priority)

            where_clause = " AND ".join(where_clauses) if where_clauses else "1=1"

            query = f"""
            SELECT COUNT(*) as count
            FROM notifications
            WHERE {where_clause}
            """

            results = self.data_base.execute_query(query, tuple(params) if params else None)

            return results[0]['count'] if results else 0

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error counting notifications: {str(e)}"
            )

    def delete_notification(self, notification_id: str) -> bool:
        """
        Delete a notification by ID

        Args:
            notification_id: UUID of the notification to delete

        Returns:
            True if deleted, False if not found
        """
        try:
            query = "DELETE FROM notifications WHERE notification_id = %s"
            rows_affected = self.data_base.execute_update(query, (notification_id,))
            return rows_affected > 0

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error deleting notification: {str(e)}"
            )

    def delete_old_notifications(self, days: int = 30) -> int:
        """
        Delete notifications older than specified days

        Args:
            days: Number of days to keep (default: 30)

        Returns:
            Number of notifications deleted
        """
        try:
            query = """
            DELETE FROM notifications
            WHERE stored_at < NOW() - INTERVAL '%s days'
            """
            rows_affected = self.data_base.execute_update(query, (days,))
            return rows_affected

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error deleting old notifications: {str(e)}"
            )
