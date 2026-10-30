(() => {
  const source = document.getElementById('signup-locations');
  const state = document.getElementById('id_state');
  const district = document.getElementById('id_district');
  if (!source || !state || !district) return;
  const locations = JSON.parse(source.textContent);
  const placeholder = district.options[0].text;
  function refresh(preserve) {
    const previous = preserve ? district.value : '';
    district.replaceChildren(new Option(placeholder, ''));
    for (const name of locations[state.value] || []) district.add(new Option(name, name));
    district.value = (locations[state.value] || []).includes(previous) ? previous : '';
  }
  state.addEventListener('change', () => refresh(false));
  // Retain a valid selection after server-side validation errors or history navigation.
  window.addEventListener('pageshow', () => refresh(true));
  refresh(true);
})();
