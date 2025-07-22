/**
 * Retry and Timeout Utilities
 * 
 * Provides utilities for wrapping async functions with retry logic,
 * exponential backoff, and timeout fallbacks.
 */

export interface RetryOptions {
  maxRetries?: number;
  baseDelay?: number;
  maxDelay?: number;
  backoffMultiplier?: number;
  timeoutMs?: number;
}

export interface RetryResult<T> {
  data: T;
  attempts: number;
  totalTime: number;
}

/**
 * Default retry configuration
 */
const DEFAULT_RETRY_OPTIONS: Required<RetryOptions> = {
  maxRetries: 3,
  baseDelay: 500,
  maxDelay: 10000,
  backoffMultiplier: 2,
  timeoutMs: 10000,
};

/**
 * Calculate delay for exponential backoff
 */
function calculateDelay(attempt: number, options: Required<RetryOptions>): number {
  const delay = options.baseDelay * Math.pow(options.backoffMultiplier, attempt);
  return Math.min(delay, options.maxDelay);
}

/**
 * Wraps an async function with retry logic and exponential backoff
 */
export async function withRetry<T>(
  fn: () => Promise<T>,
  options: RetryOptions = {}
): Promise<RetryResult<T>> {
  const config = { ...DEFAULT_RETRY_OPTIONS, ...options };
  const startTime = Date.now();
  let lastError: Error | undefined;

  for (let attempt = 0; attempt <= config.maxRetries; attempt++) {
    try {
      const data = await withTimeout(fn(), config.timeoutMs);
      return {
        data,
        attempts: attempt + 1,
        totalTime: Date.now() - startTime,
      };
    } catch (error) {
      lastError = error instanceof Error ? error : new Error(String(error));
      
      // Don't retry on the last attempt
      if (attempt === config.maxRetries) {
        break;
      }

      // Don't retry on certain error types
      if (isNonRetryableError(lastError)) {
        break;
      }

      // Wait before retrying (exponential backoff)
      const delay = calculateDelay(attempt, config);
      await new Promise(resolve => setTimeout(resolve, delay));
    }
  }

  throw new Error(
    `Request failed after ${config.maxRetries + 1} attempts. Last error: ${lastError?.message || 'Unknown error'}`
  );
}

/**
 * Wraps a promise with a timeout
 */
export function withTimeout<T>(
  promise: Promise<T>,
  timeoutMs: number
): Promise<T> {
  return Promise.race([
    promise,
    new Promise<never>((_, reject) => {
      setTimeout(() => {
        reject(new Error(`Request timed out after ${timeoutMs}ms`));
      }, timeoutMs);
    }),
  ]);
}

/**
 * Determines if an error should not be retried
 */
function isNonRetryableError(error: Error): boolean {
  // Don't retry on authentication errors (401)
  if (error.message.includes('401') || error.message.includes('Unauthorized')) {
    return true;
  }

  // Don't retry on permission errors (403)
  if (error.message.includes('403') || error.message.includes('Forbidden')) {
    return true;
  }

  // Don't retry on validation errors (400)
  if (error.message.includes('400') || error.message.includes('Bad Request')) {
    return true;
  }

  // Don't retry on not found errors (404)
  if (error.message.includes('404') || error.message.includes('Not Found')) {
    return true;
  }

  return false;
}

/**
 * Utility to create a retryable function with custom options
 */
export function createRetryableFunction<T>(
  fn: (...args: unknown[]) => Promise<T>,
  options: RetryOptions = {}
): (...args: unknown[]) => Promise<RetryResult<T>> {
  return async (...args: unknown[]) => {
    return withRetry(() => fn(...args), options);
  };
}

/**
 * Utility to create a timeout wrapper for any async function
 */
export function createTimeoutWrapper<T>(
  fn: (...args: unknown[]) => Promise<T>,
  timeoutMs: number
): (...args: unknown[]) => Promise<T> {
  return async (...args: unknown[]) => {
    return withTimeout(fn(...args), timeoutMs);
  };
} 