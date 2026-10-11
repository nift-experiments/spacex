/* Reference-only unavailable-service fixture. No token, challenge or submission.
 * The real SDK requires its canonical host and cannot initialize offline.
 * This fixture lets the delivered site's surrounding form UI initialize.
 */
var turnstile = window.turnstile = {
  render: () => 'offline-reference-unavailable',
  reset: () => {},
  remove: () => {},
  execute: () => {},
  getResponse: () => '',
  isExpired: () => true,
};
