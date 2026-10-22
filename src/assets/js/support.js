(function () {
  'use strict';
  var cfg = document.getElementById('site'), ar = cfg && cfg.dataset.lang === 'ar';
  var wa = cfg && cfg.dataset.wa;
  function digits(s) { return s.replace(/[٠-٩۰-۹]/g, function(c) { return String(c.charCodeAt(0) - (c <= '٩' ? 1632 : 1776)); }); }
  window.s99Phone = function (form, prefix) {
    var code = form.elements[prefix + '-country'].value;
    var input = form.elements[prefix + '-phone'];
    var raw = digits(input.value.trim());
    var number = raw.replace(/[\s()\-]/g, '').replace(/^0/, '');
    var rules = {20:/^1[0125]\d{8}$/,966:/^5\d{8}$/,971:/^5[024568]\d{7}$/,973:/^[36]\d{7}$/,968:/^[79]\d{7}$/,962:/^7[789]\d{7}$/,965:/^[569]\d{7}$/,974:/^[3567]\d{7}$/,1:/^[2-9]\d{2}[2-9]\d{6}$/,44:/^7\d{9}$/};
    var ok = code && /^[\d\s()\-]+$/.test(raw) && rules[code] && rules[code].test(number) && !/(\d)\1{6}/.test(number);
    input.setAttribute('aria-invalid', ok ? 'false' : 'true');
    return ok ? '+' + code + number : '';
  };
  window.s99PhoneError = ar ? 'اختار كود الدولة واكتب رقم موبايل صحيح متوافق مع الدولة، بدون كود الدولة.' : 'Select a country code and enter a valid mobile number for that country, without its country code.';
  var launch = document.getElementById('support-launch'), panel = document.getElementById('support-panel');
  if (!launch || !panel) return;
  var log = document.getElementById('support-messages'), question = document.getElementById('support-question');
  var field = document.getElementById('support-input'), handoff = document.getElementById('support-handoff');
  var count = 0, history = [], lastQuestion = '';
  var visitor = null, identity = document.getElementById('support-identity');
  identity.addEventListener('submit', function(e) {
    e.preventDefault();
    var name = this.elements['visitor-name'].value.trim(), phone = window.s99Phone(this, 'visitor');
    var error = this.querySelector('.form-error');
    if (name.length < 2) { error.textContent = ar ? 'اكتب اسمك (حرفين على الأقل).' : 'Please enter your name (at least two characters).'; return; }
    if (!phone) { error.textContent = window.s99PhoneError; return; }
    visitor = {name:name, phone:phone}; error.textContent = ''; this.hidden = true;
    document.getElementById('support-chat').hidden = false;
    var lead = document.getElementById('support-lead');
    lead.elements['lead-name'].value = name;
    lead.elements['lead-country'].value = this.elements['visitor-country'].value;
    lead.elements['lead-phone'].value = this.elements['visitor-phone'].value;
    field.focus();
  });
  function message(text, user) {
    var p = document.createElement('p'); p.className = user ? 'support-user' : 'support-answer'; p.textContent = text;
    log.appendChild(p); log.scrollTop = log.scrollHeight;
  }
  function offer() {
    handoff.hidden = false;
    var summary = (ar ? 'أهلًا S99، عايز أتكلم مع الفريق عن:\n' : 'Hi S99, I would like to speak to your team about:\n') + history.slice(-6).join('\n');
    summary += '\n' + (ar ? 'الاسم: ' : 'Name: ') + visitor.name + '\n' + visitor.phone;
    document.getElementById('support-wa').href = 'https://wa.me/' + wa + '?text=' + encodeURIComponent(summary);
  }
  function answer(q, topic) {
    if (!visitor) return;
    message(q, true); history.push(q); lastQuestion = q; count++;
    var detail = /campaign|budget|price|pricing|quote|book|package|proposal|ك[ام]مبين|كامبين|حمل[ةه]|ميزاني|سعر|اسعار|أسعار|باق[ةه]|باقات|تكلف|اشترك|اشتراك|حجز|تفاصيل|تواصل|رقمي|callback|details|contact/i.test(q);
    if (detail || count > 3) {
      message(ar ? 'تفاصيل الحملة والتكلفة المناسبة محتاجة الفريق يعرف هدفك ونشاطك. تقدر تكمل على واتساب، أو تسيب رقمك في طلب تواصل. اضغط الخيار المناسب تحت.' : 'Your campaign details and pricing need a conversation with our team about your brand and goals. Continue on WhatsApp or request a callback below.'); offer(); return;
    }
    if (topic === 'achievements' || /إنجاز|انجاز|اعمال|أعمال|عملاء|نتائج|achievement|client|work|result/i.test(q)) {
      message(ar ? 'بحسب معرضنا: اشتغلنا على أكثر من 100 مشروع لأكثر من 45 علامة، ومنها Muhrah Maison و777 Lounge وCLAV 57 وKonga Lounge. وعندنا أعمال وحملات مع صنّاع محتوى عبر 6 دول. تقدر تشوف الفيديوهات في قسم أعمالنا.' : 'Our portfolio includes 100+ projects for 45+ brands, with work for Muhrah Maison, 777 Lounge, CLAV 57 and Konga Lounge, plus creator campaigns across six countries. Explore the Work section to watch our productions.');
    } else if (topic === 'services' || /خدم|تصوير|مونتاج|سوشيال|مؤثر|service|production|social|influencer/i.test(q)) {
      message(ar ? 'خدماتنا: إدارة السوشيال ميديا والمحتوى والإعلانات، التصوير والإنتاج والمونتاج، وحملات المؤثرين. فريق واحد للتخطيط والإنتاج والنشر والمتابعة، حسب احتياج كل نشاط.' : 'We offer social media management, content and paid ads, media production and editing, and influencer campaigns. One team handles strategy, production, publishing and reporting around your brand’s needs.');
    } else if (topic === 'company' || /شرك|مين|عنكم|تأس|مقر|دول|مكان|company|about|where|who|founded/i.test(q)) {
      message(ar ? 'S99 وكالة تسويق وإنتاج إعلامي أسسها أحمد صالح سنة 2024. مقرنا في العجوزة بالجيزة، وبنشتغل مع علامات في مصر والسعودية والبحرين والإمارات. فريقنا الداخلي بيجمع الاستراتيجية والمحتوى والإنتاج والإعلانات.' : 'S99 is a marketing and media production agency founded by Ahmed Saleh in 2024, based in Agouza, Giza. We work with brands in Egypt, Saudi Arabia, Bahrain and the UAE, combining strategy, content, production and ads.');
    } else {
      message(ar ? 'أقدر أساعدك بالمعلومات المنشورة عن الشركة وخدماتنا وأعمالنا. السؤال ده الأفضل يرد عليه الفريق مباشرة على واتساب، أو تقدر تطلب التواصل.' : 'I can help with published information about S99, our services and portfolio. Our team can answer this question directly on WhatsApp, or you can request a callback.'); offer(); return;
    }
    if (count >= 3) { message(ar ? 'جاهز نتكلم عن مشروعك؟ تقدر دلوقتي تكمل التفاصيل مع الفريق على واتساب أو تطلب التواصل.' : 'Ready to discuss your project? Continue with our team on WhatsApp or request a callback.'); offer(); }
  }
  message(ar ? 'أهلًا! اسألني عن S99 وخدماتنا وإنجازاتنا. أنا مساعد للمعلومات المنشورة، وتفاصيل الحملات بيكملها معاك فريقنا.' : 'Welcome! Ask about S99, our services and portfolio. I help with published company information; our team handles campaign specifics.');
  function close() { panel.hidden = true; launch.setAttribute('aria-expanded', 'false'); launch.focus(); }
  launch.addEventListener('click', function () { panel.hidden = !panel.hidden; launch.setAttribute('aria-expanded', String(!panel.hidden)); if (!panel.hidden) { if(visitor) field.focus(); else identity.elements['visitor-name'].focus(); } });
  document.getElementById('support-close').addEventListener('click', close);
  panel.addEventListener('keydown', function(e) { if(e.key === 'Escape') close(); });
  question.addEventListener('submit', function(e) { e.preventDefault(); var q = field.value.trim(); if (!q) return; field.value = ''; answer(q); });
  panel.querySelectorAll('[data-topic]').forEach(function(b) { b.addEventListener('click', function() { answer(b.textContent, b.dataset.topic); }); });
  document.getElementById('support-callback').addEventListener('click', function() { var f = document.getElementById('support-lead'); f.hidden = false; f.elements['lead-name'].focus(); });
  document.getElementById('support-lead').addEventListener('submit', function(e) {
    e.preventDefault(); var phone = window.s99Phone(this, 'lead'), error = this.querySelector('.form-error');
    if (!phone) { error.textContent = window.s99PhoneError; return; }
    error.textContent = '';
    var text = (ar ? 'طلب تواصل من موقع S99\nالاسم: ' : 'S99 website callback request\nName: ') + this.elements['lead-name'].value.trim() + '\n' + phone + '\n' + lastQuestion;
    var link = 'https://wa.me/' + wa + '?text=' + encodeURIComponent(text);
    window.open(link, '_blank', 'noopener');
  });
})();
