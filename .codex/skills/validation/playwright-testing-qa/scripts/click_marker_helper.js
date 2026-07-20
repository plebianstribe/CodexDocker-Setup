'use strict';

async function markerAt(page, x, y, label) {
  await page.evaluate(
    ({ markerX, markerY, markerLabel }) => {
      const marker = document.createElement('div');
      marker.className = 'imp-upload-click-marker';
      marker.style.position = 'fixed';
      marker.style.left = `${markerX - 8}px`;
      marker.style.top = `${markerY - 8}px`;
      marker.style.width = '16px';
      marker.style.height = '16px';
      marker.style.borderRadius = '50%';
      marker.style.background = '#d80b0b';
      marker.style.border = '2px solid #ffffff';
      marker.style.boxShadow = '0 0 0 2px rgba(216, 11, 11, 0.25)';
      marker.style.zIndex = '2147483647';
      marker.style.pointerEvents = 'none';
      marker.title = markerLabel || 'click';
      document.body.appendChild(marker);
    },
    { markerX: x, markerY: y, markerLabel: label },
  );
}

async function centerForSelector(page, selector) {
  const locator = page.locator(selector);
  const box = await locator.boundingBox();
  if (!box) {
    throw new Error(`Unable to locate bounding box for selector: ${selector}`);
  }
  return {
    x: Math.round(box.x + box.width / 2),
    y: Math.round(box.y + box.height / 2),
  };
}

module.exports = {
  markerAt,
  centerForSelector,
};
