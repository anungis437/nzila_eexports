import * as Sentry from '@sentry/react';

/**
 * Simple error button from Sentry docs to test error tracking
 * This component should be removed before production deployment
 */
export function ErrorButton() {
  return (
    <button
      onClick={() => {
        throw new Error('This is your first error!');
      }}
      className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-md font-medium"
    >
      Break the world
    </button>
  );
}

/**
 * Alternative test button with custom styling
 */
export function SentryTestButton() {
  return (
    <button
      onClick={() => {
        throw new Error('Sentry Test: This is your first error!');
      }}
      className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-md font-medium"
    >
      🐛 Test Sentry Error
    </button>
  );
}

/**
 * Test button for Sentry performance monitoring
 */
export function SentryPerformanceTest() {
  const handleClick = () => {
    Sentry.startSpan(
      {
        op: 'ui.click',
        name: 'Performance Test Button Click',
      },
      (span) => {
        span.setAttribute('test_type', 'performance');
        span.setAttribute('component', 'SentryPerformanceTest');
        
        // Simulate some work
        const start = Date.now();
        while (Date.now() - start < 100) {
          // Busy wait for 100ms
        }
        
        Sentry.captureMessage('Performance test completed', 'info');
      },
    );
  };

  return (
    <button
      onClick={handleClick}
      className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md font-medium"
    >
      ⚡ Test Sentry Performance
    </button>
  );
}

/**
 * Test button for Sentry exception capture
 */
export function SentryExceptionTest() {
  const handleClick = () => {
    try {
      // Simulate an API error
      throw new Error('API Error: Failed to fetch user data');
    } catch (error) {
      Sentry.captureException(error, {
        tags: {
          test: true,
          component: 'SentryExceptionTest',
        },
        extra: {
          userId: 123,
          endpoint: '/api/users/123',
        },
      });
      
      console.error('Caught and sent to Sentry:', error);
    }
  };

  return (
    <button
      onClick={handleClick}
      className="px-4 py-2 bg-yellow-600 hover:bg-yellow-700 text-white rounded-md font-medium"
    >
      ⚠️ Test Sentry Exception
    </button>
  );
}

/**
 * Combined test component with all Sentry tests
 */
export default function SentryTestPanel() {
  return (
    <div className="fixed bottom-4 right-4 p-4 bg-gray-900 rounded-lg shadow-lg space-y-2">
      <h3 className="text-white font-semibold mb-2">Sentry Tests (Dev Only)</h3>
      <div className="flex flex-col space-y-2">
        <ErrorButton />
        <SentryPerformanceTest />
        <SentryExceptionTest />
      </div>
      <p className="text-xs text-gray-400 mt-2">Remove before production</p>
    </div>
  );
}
