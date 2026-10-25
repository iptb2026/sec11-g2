// Uses tests/browser_api.py only. Never changes existing bank records.
const { chromium } = require('playwright');
const assert = require('node:assert/strict');
(async()=>{
 let debugPage;
 const browser=await chromium.launch({headless:process.env.BEMBANK_HEADED!=='1',args:['--no-sandbox']});
 try {
 const page=await browser.newPage({viewport:{width:1440,height:1000}}), errors=[];
 debugPage=page;page.setDefaultTimeout(20000);
 page.on('pageerror',e=>errors.push(e.message));page.on('console',m=>{if(m.type()==='error')errors.push(m.text())});
 await page.context().addInitScript(()=>{window.print=()=>{window.printCalled=true}});
 await page.route('**/bembank/api/**',async route=>{const url=new URL(route.request().url());const path=url.pathname.replace('/bembank/api','')+url.search;const response=await route.fetch({url:'http://127.0.0.1:5012'+path});if(response.status()>=400)errors.push(path+': '+response.status());await route.fulfill({response})});
 const goto=async(path,title)=>{await page.goto('http://127.0.0.1:9000/bembank/#'+path);await page.reload();await page.getByRole('heading',{name:title,exact:true}).waitFor();await page.waitForLoadState('networkidle')};
 const login=async(name)=>{await goto('/login','Welcome back');await page.getByLabel('Username',{exact:true}).fill(name);await page.getByLabel('Password',{exact:true}).fill('test-password-123');await page.getByRole('button',{name:'Sign in',exact:true}).click();await page.getByRole('heading',{name:/Welcome back,/}).waitFor()};
 await login('staff');await goto('/staff/register','Register a customer');
 for(const [label,value] of Object.entries({'First name':'Project','Last name':'Customer','Username':'projectcustomer','Initial password':'Project-secret-123','Email':'project@example.com'}))await page.getByLabel(label,{exact:true}).fill(value);
 await page.getByLabel('Account type',{exact:true}).click();await page.getByRole('option',{name:'Family savings account',exact:true}).click();
 await page.getByRole('button',{name:'Create customer and account',exact:true}).click();await page.getByRole('heading',{name:'Customer registered'}).waitFor();
 console.log('PASS: staff creates customer and Family Savings account');
 await page.getByRole('button',{name:'Sign out',exact:true}).first().click();await login('alice');
 await goto('/customer/other-banks','Send to another bank');
 for(const [label,option] of [['From account','BEM0001'],['Destination bank','Northstar Bank']]){await page.getByLabel(label,{exact:true}).click();await page.getByRole('option',{name:option,exact:true}).click()}
 await page.getByLabel('Recipient account number').fill('DEMO12345');await page.getByLabel('Recipient name').fill('Recipient');await page.getByLabel('Amount (PHP)',{exact:true}).fill('125.50');
 await page.getByRole('button',{name:'Review transfer',exact:true}).click();await page.getByRole('heading',{name:'Confirm other-bank transfer'}).waitFor();await page.getByRole('button',{name:'Confirm transfer',exact:true}).click();await page.locator('td').filter({hasText:/^PROCESSING$/}).waitFor();
 console.log('PASS: reviewed other-bank transfer and processing history');
 await goto('/statements','Account statements');await page.getByRole('button',{name:'Generate',exact:true}).click();await page.getByText('INTERBANK TRANSFER',{exact:true}).waitFor();
 const download=page.waitForEvent('download');await page.getByRole('button',{name:'Export CSV'}).click();assert.ok((await download).suggestedFilename().endsWith('.csv'));
 const popupPromise=page.waitForEvent('popup');await page.getByRole('button',{name:'Print / Save PDF'}).click();const popup=await popupPromise;await popup.waitForLoadState();assert.ok((await popup.locator('body').innerText()).includes('INTERBANK TRANSFER'));await popup.close();
 console.log('PASS: ledger report, CSV download, printable PDF document');
 await page.setViewportSize({width:390,height:844});
 for(const [path,title] of [['/statements','Account statements'],['/customer/other-banks','Send to another bank']]){await goto(path,title);assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1))}
 assert.deepEqual(errors,[]);console.log('PASS: new customer screens at mobile width; no browser or API errors');
 }catch(e){if(debugPage) console.log('Form feedback:',await debugPage.locator('.q-field__messages,.bank-feedback').allTextContents());throw e}finally{await browser.close()}
})().catch(e=>{console.error(e);process.exit(1)});
