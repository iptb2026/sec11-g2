export const passwordChecks = value => {
  const text = value || ''
  return [
    { label: 'At least 12 characters', met: [...text].length >= 12 },
    { label: 'An uppercase letter (A–Z)', met: /[A-Z]/.test(text) },
    { label: 'A lowercase letter (a–z)', met: /[a-z]/.test(text) },
    { label: 'A number (0–9)', met: /[0-9]/.test(text) },
    { label: 'A symbol, such as ! @ # $', met: /[!"#$%&'()*+,\-./:;<=>?@[\]\\^_`{|}~]/.test(text) },
  ]
}
export const passwordRule = value => passwordChecks(value).every(check => check.met) || 'Complete all password requirements below.'
