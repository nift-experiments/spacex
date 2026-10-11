// Real pinned launch records and delivered clock/date semantics, with fixed test time.
const assert=require('node:assert/strict');
const {siteDate,count,presentation}=require('../../public/assets/js/launch-clock.js');
const {launches}=require('../../public/assets/data/launch-schedule.json');
const now=Date.parse('2026-10-12T00:00:00Z');
assert.equal(siteDate('2026-10-01T11:10:00','SLC-40, Florida').toISOString(),'2026-10-01T15:10:00.000Z');
assert.equal(siteDate('2026-01-01T11:10:00','SLC-40, Florida').toISOString(),'2026-01-01T16:10:00.000Z');
assert.equal(presentation(launches['sl-15-25'],false,false,now).text,'October 13, 2026 10:00 - 14:00 Melbourne Time');
assert.equal(presentation(launches.crs35,false,false,now).text,'October 13, 2026 21:33 Melbourne Time');
assert.equal(presentation(launches.ussf481,false,false,now).text,'October 16, 2026 10:44 - 14:44 Melbourne Time');
assert.equal(presentation(launches['sl-15-25'],true,false,now).mode,'countdown');
assert.ok(count(launches.crew13,now)>0);
assert.ok(count(launches['sl-15-25'],now)<0);
assert.equal(count({timings:{TZeroLaunchDate:{Seconds:1},TZeroPaused:true,TZeroValue:-12}},now),-12);
assert.equal(presentation(launches['sl-15-25'],false,true,now).text,'October 13, 2026');
assert.equal(presentation(launches.demo2,false,false,now).text,'May 30, 2020 - August 2, 2020');
console.log('Pinned launch clock/date cases pass');
