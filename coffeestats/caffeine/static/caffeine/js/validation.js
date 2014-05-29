/* global $, gettext */

var emailpat = /^([A-Za-z0-9._%+-]+)@([^@]+)$/;
var usernamepat = /^[a-z][a-z0-9_-]{1,29}$/;

function sanitize_not_empty(fieldspec, message) {
  "use strict";
  var nefield = $(fieldspec);
  var nevalue = $.trim(nefield.val());
  if (nevalue.length === 0) {
    alert(message);
    nefield.focus();
    return false;
  }
  nefield.val(nevalue);
  return true;
}

function emailfieldvalidation(event) {
  if (this.validity.patternMismatch) {
    this.setCustomValidity(gettext('Email address must contain a local part and a domain part separated by an @ sign!'));
  } else if (this.validity.valueMissing) {
    this.setCustomValidity(gettext('Email address must not be empty!'));
  } else {
    this.setCustomValidity('');
  }
}

function sanitize_email(fieldspec, mandatory) {
  "use strict";
  mandatory = typeof mandatory !== 'undefined' ? mandatory : true;
  var emfield = $(fieldspec);
  var emvalue = $.trim(emfield.val());
  if ((emvalue.length === 0) && mandatory) {
    alert(gettext('Email address must not be empty!'));
    emfield.focus();
    return false;
  }
  if (emailpat.test(emvalue)) {
    emfield.val(emvalue);
    return true;
  }
  alert(gettext('Email address must contain a local part and a domain part separated by an @ sign!'));
  emfield.focus();
  return false;
}

function pwfieldvalidation(event) {
  if (this.validity.valueMissing) {
    this.setCustomValidity(gettext('Password must not be empty!'));
  } else if (this.validity.patternMismatch) {
    this.setCustomValidity(gettext('Password must be at least 8 characters long!'));
  } else {
    this.setCustomValidity('');
  }
}

function sanitize_password(pwfieldspec, repfieldspec, allowempty) {
  "use strict";
  allowempty = typeof allowempty !== 'undefined' ? allowempty : false;
  var pwfield = $(pwfieldspec);
  var repfield = $(repfieldspec);
  var pwval = $.trim(pwfield.val());
  var repval = $.trim(repfield.val());

  pwfield.val(pwval);
  repfield.val(repval);

  if (!allowempty && (pwval.length == 0)) {
    alert(gettext('Password must not be empty!'));
    pwfield.focus();
    return false;
  }

  if ((pwval.length > 0) && (pwval.length < 8)) {
    alert(gettext('Password must be at least 8 characters long!'));
    pwfield.focus();
    return false;
  }
  if (pwval != repval) {
    alert(gettext('Passwords must match!'));
    repfield.focus();
    return false;
  }
  return true;
}

function sanitize_string(fieldspec, mandatory, fieldname) {
  "use strict";
  mandatory = typeof mandatory !== 'undefined' ? mandatory : true;
  fieldname = typeof fieldname !== 'undefined' ? fieldname : 'Field';
  var stfield = $(fieldspec);
  var stvalue = $.trim(stfield.val());
  if ((stvalue.length == 0) && mandatory) {
    msgfmt = gettext('%(fieldname)s must not be empty!');
    alert(interpolate(msgfmt, {fieldname: fieldname}, true));
    stfield.focus();
    return false;
  }
  return true;
}

function usernamefieldvalidation(event) {
  if (this.validity.patternMismatch) {
    this.setCustomValidity(gettext('Invalid username! A username has at least 3 characters, starting with a letter. It may consist of letters, digits, hypens and underscores.'));
  } else if (this.validity.valueMissing) {
    this.setCustomValidity(gettext('Username must not be empty!'));
  } else {
    this.setCustomValidity('');
  }
}

function sanitize_username(fieldspec) {
  "use strict";
  var unfield = $(fieldspec);
  var unvalue = $.trim(unfield.val());
  if (unvalue.length == 0) {
    alert('Username must not be empty!');
    unfield.focus();
    return false;
  }
  if (usernamepat.test(unvalue)) {
    unfield.val(unvalue);
    return true;
  }
  alert(gettext('Invalid username! A username has at least 3 characters, starting with a letter. It may consist of letters, digits, hypens and underscores.'));
  unfield.focus();
  return false;
}

function pad(n) {
  "use strict";
  return n<10 ? '0'+n : n;
}

function coffeedate(d) {
  "use strict";
  return d.getFullYear() + '-' +
    pad(d.getMonth() + 1) + '-' +
    pad(d.getDate());
}

function coffeetime(d) {
  "use strict";
  return pad(d.getHours()) + ':' +
    pad(d.getMinutes()) +':' +
    pad(d.getSeconds());
}

var datepat = /^([0-9]{4})-([0-9]{1,2})-([0-9]{1,2})$/;
var timepat = /^([0-9]{1,2}):([0-9]{1,2})(|:([0-9]{1,2}))$/;

function sanitize_datetime(datefieldspec, timefieldspec) {
  "use strict";
  var dfield = $(datefieldspec);
  var tfield = $(timefieldspec);
  var dval = $.trim(dfield.val());
  var tval = $.trim(tfield.val());
  var now = new Date();
  if (dval.length === 0) {
    dval = coffeedate(now);
    dfield.val(dval);
  }
  if (tval.length === 0) {
    tval = coffeetime(now);
    tfield.val(tval);
  }
  var dmatches = datepat.exec(dval);
  var tmatches = timepat.exec(tval);

  if (dmatches !== null && tmatches !== null) {
    var year, month, day, hour, minute, second;
    year = parseInt(dmatches[1]);
    month = parseInt(dmatches[2]);
    day = parseInt(dmatches[3]);
    hour = parseInt(tmatches[1]);
    minute = parseInt(tmatches[2]);
    second = (tmatches[3] !== "") ? parseInt(tmatches[4]) : 0;
    var entered = new Date(year, month -1 , day, hour, minute, second);
    if (entered.getTime() <= now.getTime()) {
      dfield.val(dval);
      tfield.val(tval);
      return true;
    }
    alert(gettext('You can not enter dates in the future!'));
  } else {
    if (dmatches === null) {
      alert(gettext('No valid date information. Expected format YYYY-mm-dd'));
    }
    if (tmatches === null) {
      alert(gettext('No valid time information. Expected format HH:MM:ss'));
    }
  }
  dfield.focus();
  return false;
}
