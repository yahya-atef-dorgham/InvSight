import { VoiceQuery } from '../types/voice';

/**
 * Offline query queue for voice queries when network is unavailable.
 */
class OfflineQueue {
  private queue: VoiceQuery[] = [];
  private readonly STORAGE_KEY = 'voice_query_queue';

  constructor() {
    this.loadQueue();
  }

  private loadQueue(): void {
    try {
      const stored = localStorage.getItem(this.STORAGE_KEY);
      if (stored) {
        this.queue = JSON.parse(stored);
      }
    } catch (error) {
      console.error('Failed to load offline queue:', error);
      this.queue = [];
    }
  }

  private saveQueue(): void {
    try {
      localStorage.setItem(this.STORAGE_KEY, JSON.stringify(this.queue));
    } catch (error) {
      console.error('Failed to save offline queue:', error);
    }
  }

  enqueue(query: VoiceQuery): void {
    this.queue.push(query);
    this.saveQueue();
  }

  dequeue(): VoiceQuery | undefined {
    const query = this.queue.shift();
    if (query) {
      this.saveQueue();
    }
    return query;
  }

  getAll(): VoiceQuery[] {
    return [...this.queue];
  }

  clear(): void {
    this.queue = [];
    this.saveQueue();
  }

  get length(): number {
    return this.queue.length;
  }
}

export const offlineQueue = new OfflineQueue();

/**
 * Check if device is online.
 */
export const isOnline = (): boolean => {
  return navigator.onLine;
};

/**
 * Process queued queries when connection is restored.
 */
export const processQueue = async (
  processQuery: (query: VoiceQuery) => Promise<void>
): Promise<void> => {
  if (!isOnline()) {
    return;
  }

  while (offlineQueue.length > 0) {
    const query = offlineQueue.dequeue();
    if (query) {
      try {
        await processQuery(query);
      } catch (error) {
        console.error('Failed to process queued query:', error);
        // Re-queue if processing fails
        offlineQueue.enqueue(query);
        break;
      }
    }
  }
};
