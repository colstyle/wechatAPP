Component({
  properties: {
    hoursLeft: { type: Number, value: 0 },
    totalHours: { type: Number, value: 24 }
  },
  data: { degrees: 0 },
  observers: {
    'hoursLeft, totalHours': function(h, t) {
      if (t <= 0) return;
      let p = h / t;
      if (p < 0) p = 0;
      if (p > 1) p = 1;
      this.setData({ degrees: parseInt(360 * p) });
    }
  }
})