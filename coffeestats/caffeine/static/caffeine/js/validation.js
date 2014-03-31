var emailpat = /^([A-Za-z0-9._%+-]+)@([^@]+)$/;
var usernamepat = /^[a-z][a-z0-9_-]{1,29}$/;

function sanitize_not_empty(fieldspec, message) {
  var nefield = $(fieldspec);
  var nevalue = $.trim(nefield.val());
  if (nevalue.length == 0) {
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
  mandatory = typeof mandatory !== 'undefined' ? mandatory : true;
  var emfield = $(fieldspec);
  var emvalue = $.trim(emfield.val());
  if ((emvalue.length == 0) && mandatory) {
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
  return n<10 ? '0'+n : n;
}

function coffeetime(d) {
  return d.getFullYear() + '-' +
    pad(d.getMonth() + 1) +'-' +
    pad(d.getDate()) + ' ' +
    pad(d.getHours()) + ':' +
    pad(d.getMinutes()) +':' +
    pad(d.getSeconds());
}

var datetimepat = /^([0-9]{4})-([0-9]{1,2})-([0-9]{1,2})\ ([0-9]{1,2}):([0-9]{1,2})(|:([0-9]{1,2}))$/;

function sanitize_datetime(fieldspec) {
  var dtfield = $(fieldspec);
  var dtval = $.trim(dtfield.val());
  var now = new Date();
  if (dtval.length == 0) {
    dtval = coffeetime(now);
    dtfield.val(dtval);
  }
  var matches = datetimepat.exec(dtval);
  if (matches !== null) {
    var year, month, day, hour, minute, second;
    year = parseInt(matches[1]);
    month = parseInt(matches[2]);
    day = parseInt(matches[3]);
    hour = parseInt(matches[4]);
    minute = parseInt(matches[5]);
    second = (matches[6] != "") ? parseInt(matches[7]) : 0;
    var entered = new Date(year, month -1 , day, hour, minute, second);
    if (entered.getTime() <= now.getTime()) {
      dtfield.val(dtval);
      return true;
    }
    alert(gettext('You can not enter dates in the future!'));
  } else {
    alert(gettext('No valid date/time information. Expected format YYYY-mm-dd HH:MM:ss'));
  }
  dtfield.focus();
  return false;
}
