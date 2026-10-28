export function filterOptions (options, query) {
  const needle = String(query || '').trim().toLocaleLowerCase()
  if (!needle) return options
  return options.filter(option => [option?.label ?? option, option?.holder].filter(Boolean).join(' ').toLocaleLowerCase().includes(needle))
}

export function optionLabel (options, value) {
  const option = options.find(item => item.value === value)
  return option ? [option.label, option.holder].filter(Boolean).join(' — ') : `#${value}`
}
