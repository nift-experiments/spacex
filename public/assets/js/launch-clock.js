/* Bounded adaptation of delivered launch-time/countdown rules; maintained CMS inputs. */
(() => {
  const standard = new Map([['LC-39A, FLORIDA','-05:00'],['SLC-40, FLORIDA','-05:00'],['SLC-4E, CALIFORNIA','-08:00'],['STARBSE, TEXAS','-06:00'],['PAD 1, STARBASE','-06:00'],['PAD 2, STARBASE','-06:00'],['STARBASE PAD 1','-06:00'],['STARBASE PAD 2','-06:00'],['OMELEK ISLAND','+12:00']]);
  const daylight = new Map([...standard].map(([site,offset]) => [site, site === 'OMELEK ISLAND' ? offset : '-'+String(Number(offset.slice(1,3))-1).padStart(2,'0')+':00']));
  const zoneOffset = date => {
    const parts = new Intl.DateTimeFormat('en-US',{timeZone:'America/New_York',year:'numeric',month:'2-digit',day:'2-digit',hour:'2-digit',minute:'2-digit',second:'2-digit',hour12:false}).formatToParts(date);
    const get = key => Number(parts.find(p => p.type === key).value);
    return (date.getTime()-Date.UTC(get('year'),get('month')-1,get('day'),get('hour')%24,get('minute'),get('second')))/60000;
  };
  const siteDate = (text,site) => {
    const date = new Date(text), year = date.getUTCFullYear();
    const dst = zoneOffset(date) < Math.max(zoneOffset(new Date(Date.UTC(year,0,1))),zoneOffset(new Date(Date.UTC(year,6,1))));
    const offset = (dst ? daylight : standard).get((site || '').toUpperCase());
    return offset ? new Date(text+offset) : date;
  };
  const count = (launch,now) => {
    const o=launch.override || {},t=launch.timings || {};
    if(o.date && o.time) return Math.round((now-siteDate(`${o.date}T${o.time}`,launch.launchSite).getTime())/1000);
    if(o.windowOpenDate && o.windowOpenTime) return Math.round((now-siteDate(`${o.windowOpenDate}T${o.windowOpenTime}`,launch.launchSite).getTime())/1000);
    if(t.TZeroLaunchDate) return t.TZeroPaused ? t.TZeroValue : Math.round(now/1000-t.TZeroLaunchDate.Seconds);
    if(t.PrimaryLaunchDate) return Math.round(now/1000-t.PrimaryLaunchDate.Seconds);
    return launch.launchDate && launch.launchTime ? Math.round((now-siteDate(`${launch.launchDate}T${launch.launchTime}`,launch.launchSite).getTime())/1000) : 0;
  };
  const dateOptions={year:'numeric',month:'long',day:'numeric'},timeOptions={hour:'2-digit',minute:'2-digit',hour12:false};
  const date = value => value.toLocaleDateString('en-US',dateOptions);
  const time = (value,zone=false) => value.toLocaleTimeString('en-US',zone ? {...timeOptions,timeZoneName:'shortGeneric'} : timeOptions);
  const presentation = (launch,always,mobile,now) => {
    const o=launch.override || {},t=launch.timings || {};
    const overrideText=!!o.text && !t.TZeroLaunchDate;
    const countdown=(always && launch.missionStatus !== 'final' && ((o.date&&o.time)||(o.windowOpenDate&&o.windowOpenTime)||t.PrimaryLaunchDate?.Seconds!=null||(launch.launchDate&&launch.launchTime)) && !overrideText)||!!t.TZeroLaunchDate;
    if(countdown) return {mode:'countdown',count:count(launch,now)};
    if(overrideText) return {mode:'text',text:o.text};
    const futureOverride=!!o.date && new Date(o.date).getTime()>now;
    const window=!!(o.windowOpenDate&&o.windowOpenTime&&o.windowCloseDate&&o.windowCloseTime&&new Date(`${o.windowCloseDate} ${o.windowCloseTime}`).getTime()>now)||t.PrimaryLaunchWindow?.Open?.Seconds!=null && t.PrimaryLaunchWindow?.Close?.Seconds!=null;
    if(window && !futureOverride){
      if(mobile){const value=o.windowOpenDate ? siteDate(`${o.windowOpenDate}T${o.windowOpenTime}`,launch.launchSite) : new Date(t.PrimaryLaunchDate.Seconds*1000);return {mode:'text',text:date(value)};}
      const open=o.windowOpenDate ? siteDate(`${o.windowOpenDate}T${o.windowOpenTime}`,launch.launchSite) : new Date(t.PrimaryLaunchWindow.Open.Seconds*1000);
      const close=o.windowOpenDate ? siteDate(`${o.windowCloseDate}T${o.windowCloseTime}`,launch.launchSite) : new Date(t.PrimaryLaunchWindow.Close.Seconds*1000);
      return {mode:'text',text:date(open)===date(close) ? `${date(open)} ${time(open)} - ${time(close,true)}` : `${date(open)} ${time(open,true)} - ${date(close)} ${time(close,true)}`};
    }
    if(futureOverride || t.PrimaryLaunchDate?.Seconds!=null || launch.launchDate&&launch.launchTime){
      const exact=!!(o.date&&o.time);
      const value=exact ? siteDate(`${o.date}T${o.time}`,launch.launchSite) : o.date ? new Date(o.date) : t.PrimaryLaunchDate?.Seconds!=null ? new Date(t.PrimaryLaunchDate.Seconds*1000) : new Date(launch.launchDate);
      const utc=value.toLocaleDateString('en-US',{...dateOptions,timeZone:'UTC'});
      return {mode:'text',text:exact ? `${date(value)} ${time(value,true)}` : launch.endDate ? `${utc} - ${new Date(launch.endDate).toLocaleDateString('en-US',{...dateOptions,timeZone:'UTC'})}` : utc};
    }
    return {mode:'text',text:'TBD'};
  };
  if(typeof module !== 'undefined' && module.exports) module.exports={siteDate,count,presentation};
  if(typeof document === 'undefined') return;
  const nodes=[...document.querySelectorAll('[data-mission-timing]')];
  if(!nodes.length) return;
  const schedulePath=document.currentScript.dataset.timeSchedule;
  const digit = (value,range) => {
    const host=document.createElement('span');host.dataset.sx='launch-countdown';
    const container=document.createElement('div');container.className='digit-container';container.dataset.sx='launch-countdown-digit';
    const values=document.createElement('span');values.className='digit-values';values.dataset.sx='launch-countdown-digit';values.style.top=`${-13*value}px`;
    for(let index=0;index<range;index++){const number=document.createElement('span');number.className='digit';number.dataset.sx='launch-countdown-digit';number.textContent=String(index);values.append(number);}
    container.append(values);host.append(container);return host;
  };
  const updateCounter = (node,seconds) => {
    const absolute=Math.abs(seconds),days=Math.floor(absolute/86400),hours=Math.floor(absolute/3600)%24,minutes=Math.floor(absolute/60)%60,remaining=absolute%60;
    const values=[...(days ? [...String(days)] : []).map(value=>[Number(value),10]),[Math.floor(hours/10),3],[hours%10,10],[Math.floor(minutes/10),6],[minutes%10,10],[Math.floor(remaining/10),6],[remaining%10,10]];
    const signature=days ? String(days).length : 0;
    let counter=node.querySelector('.counter');
    if(!counter || counter.dataset.dayDigits!==String(signature)){
      counter=document.createElement('span');counter.className='counter';counter.dataset.sx='launch-countdown';counter.dataset.dayDigits=String(signature);counter.style.justifyContent=node.dataset.mobileWindow==='true' && matchMedia('(max-width:959.98px)').matches ? node.getAttribute('justifymobile') || 'left' : node.getAttribute('justify') || 'right';
      const prefix=document.createElement('span');prefix.dataset.timePrefix='';counter.append(prefix);
      const text=value=>counter.append(document.createTextNode(value));
      values.forEach(([value,range],index)=>{counter.append(digit(value,range));if(index===signature-1)text(' D\u00a0 ');else if(index===signature+1 || index===signature+3)text(' : ');});
      node.replaceChildren(counter);
    }
    counter.style.justifyContent=node.dataset.mobileWindow==='true' && matchMedia('(max-width:959.98px)').matches ? node.getAttribute('justifymobile') || 'left' : node.getAttribute('justify') || 'right';
    counter.querySelector('[data-time-prefix]').textContent=seconds<0 ? ' T- ' : ' T+ ';
    counter.querySelectorAll('.digit-values').forEach((element,index)=>{element.style.top=`${-13*values[index][0]}px`;});
    node.setAttribute('aria-label',`${seconds<0?'T-':'T+'} ${days} D ${String(hours).padStart(2,'0')}:${String(minutes).padStart(2,'0')}:${String(remaining).padStart(2,'0')}`);
  };
  fetch(schedulePath).then(response=>{if(!response.ok)throw Error('Launch schedule unavailable');return response.json();}).then(schedule=>{
    const update = () => nodes.forEach(node=>{
      const launch=schedule.launches[node.dataset.missionTiming];if(!launch)return;
      const result=presentation(launch,node.dataset.alwaysCountdown==='true',node.dataset.mobileWindow==='true' && matchMedia('(max-width:959.98px)').matches,Date.now());
      if(result.mode==='countdown') updateCounter(node,result.count);
      else if(node.textContent!==result.text){node.textContent=result.text;node.removeAttribute('aria-label');}
    });
    update();setInterval(update,1000);
    // Offline comparisons consume frozen JSON; production preserves the public timing GET.
    const offline=document.querySelector('meta[name="spacex-service-mode"]')?.content==='frozen' || new URLSearchParams(location.search).get('referenceServices')==='frozen';
    if(offline)return;
    let nextRefresh=0,bust=false,processing=false;
    const intervals=[[86400,600000],[3600,60000],[120,30000],[60,10000],[20,5000],[10,2000],[3,1000]];
    const refresh = async () => {
      if(processing || Date.now()<nextRefresh)return;processing=true;
      try{
        const response=await fetch(schedule.publicTimingUrl+(bust ? `?${Math.round(Date.now()/1000)}` : ''));
        if(!response.ok)throw Error('Public launch timing unavailable');
        const timings=await response.json();schedule.timings=timings;
        for(const launch of Object.values(schedule.launches))launch.timings=timings[launch.correlationId];
        const nearest=Math.min(86400,...Object.values(timings).map(t=>Math.abs(t.TZeroPaused===true ? t.TZeroValue : t.TZeroLaunchDate?.Seconds ? Math.round(Date.now()/1000)-t.TZeroLaunchDate.Seconds : 86400)));
        const interval=Math.min(...intervals.filter(([threshold])=>threshold>=nearest).map(([,value])=>value));bust=interval<=30000;nextRefresh=Date.now()+interval;update();
      }catch(error){console.warn(error.message);nextRefresh=Date.now()+600000;}finally{processing=false;}
    };
    refresh();setInterval(refresh,1000);
  }).catch(error=>console.warn(error.message));
})();
