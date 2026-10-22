export function preferences (userId) {
  try { const data=JSON.parse(localStorage.getItem(`bembank-preferences-${userId}`)||'{}');return {hideBalance:data.hideBalance===true,reduceMotion:data.reduceMotion===true} } catch { return {hideBalance:false,reduceMotion:false} }
}
export function applyPreferences (value) { document.documentElement.classList.toggle('bank-reduce-motion',value.reduceMotion) }
export function savePreferences (userId,value) { try {localStorage.setItem(`bembank-preferences-${userId}`,JSON.stringify(value));applyPreferences(value);return true}catch{return false} }
