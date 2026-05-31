import redis.asyncio as aioredis
import json
import logging
import asyncio
from typing import Callable, Any, Dict

logger = logging.getLogger("netverseiq.event_bus")

class EventBus:
    def __init__(self, redis_url: str):
        self.redis = aioredis.from_url(redis_url, decode_responses=True)
        self.pubsub = None
        self.tasks = []

    async def publish(self, event: str, data: Dict[str, Any]):
        """Publish an event to Redis."""
        try:
            await self.redis.publish(event, json.dumps(data))
            logger.debug(f"Published event '{event}': {data}")
        except Exception as e:
            logger.error(f"Failed to publish event '{event}': {e}")

    async def subscribe(self, event: str, handler: Callable[[Dict[str, Any]], Any]):
        """Subscribe to an event and run handler in the background."""
        if self.pubsub is None:
            self.pubsub = self.redis.pubsub()
        
        await self.pubsub.subscribe(event)
        
        async def listen():
            try:
                async for message in self.pubsub.listen():
                    if message["type"] == "message":
                        try:
                            data = json.loads(message["data"])
                            if asyncio.iscoroutinefunction(handler):
                                await handler(data)
                            else:
                                handler(data)
                        except Exception as e:
                            logger.error(f"Error in event handler for '{event}': {e}")
            except Exception as e:
                logger.error(f"Event listener error for '{event}': {e}")

        task = asyncio.create_task(listen())
        self.tasks.append(task)
        logger.info(f"Subscribed to event '{event}'")

    async def close(self):
        """Close connections and cancel tasks."""
        for task in self.tasks:
            task.cancel()
        if self.pubsub:
            await self.pubsub.unsubscribe()
        await self.redis.close()
