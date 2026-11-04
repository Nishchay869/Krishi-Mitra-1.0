// Plantix Cultivation Tips · Smooth, Glitch-Free Interactivity
(() => {
  const container = document.getElementById('cultivation-tips');
  if (!container) return;

  // Tabs & Views
  const tabTask = document.getElementById('tab-btn-task');
  const tabStage = document.getElementById('tab-btn-stage');
  const tabTimeline = document.getElementById('tab-btn-timeline');
  const panelTasks = document.getElementById('view-panel-tasks');
  const panelStages = document.getElementById('view-panel-stages');
  const panelTimeline = document.getElementById('view-panel-timeline');

  const btnBackToTasks = document.getElementById('btnBackToTasks');
  const timelineTitle = document.getElementById('timelineActiveTitle');

  // Filter Pills
  const filterPills = Array.from(container.querySelectorAll('.plantix-filter-pill'));
  const visualCards = Array.from(container.querySelectorAll('.plantix-visual-card'));
  const groupBlocks = Array.from(container.querySelectorAll('.plantix-timeline-group-block'));

  // Modal Elements
  const modalBackdrop = document.getElementById('plantixModalBackdrop');
  const modalCloseBtn = document.getElementById('modalCloseBtn');
  const modalImg = document.getElementById('modalImg');
  const modalBadge = document.getElementById('modalBadge');
  const modalHeading = document.getElementById('modalHeading');
  const modalSummary = document.getElementById('modalSummary');
  const modalWhyBox = document.getElementById('modalWhyBox');
  const modalWhyText = document.getElementById('modalWhyText');
  const modalMaterialsList = document.getElementById('modalMaterialsList');
  const modalStepsList = document.getElementById('modalStepsList');
  const modalProTipBox = document.getElementById('modalProTipBox');
  const modalProTipText = document.getElementById('modalProTipText');
  const modalToolBtn = document.getElementById('modalToolBtn');
  const modalToolName = document.getElementById('modalToolName');

  let lastActiveView = 'tasks';

  // 1. Smooth, Offset Scroll Helper
  function scrollToTips() {
    const stickyHeader = document.querySelector('.site-header');
    const headerHeight = stickyHeader ? stickyHeader.offsetHeight : 60;
    const targetTop = container.getBoundingClientRect().top + window.pageYOffset - (headerHeight + 16);
    window.scrollTo({
      top: Math.max(0, targetTop),
      behavior: 'smooth'
    });
  }

  // 2. Tab Navigation Switcher
  function switchView(viewName) {
    if (tabTask) {
      tabTask.classList.toggle('active', viewName === 'tasks');
      tabTask.setAttribute('aria-selected', viewName === 'tasks');
    }
    if (tabStage) {
      tabStage.classList.toggle('active', viewName === 'stages');
      tabStage.setAttribute('aria-selected', viewName === 'stages');
    }
    if (tabTimeline) {
      tabTimeline.classList.toggle('active', viewName === 'timeline');
      tabTimeline.setAttribute('aria-selected', viewName === 'timeline');
    }

    if (panelTasks) panelTasks.hidden = (viewName !== 'tasks');
    if (panelStages) panelStages.hidden = (viewName !== 'stages');
    if (panelTimeline) panelTimeline.hidden = (viewName !== 'timeline');

    if (viewName === 'tasks' || viewName === 'stages') {
      lastActiveView = viewName;
    }
  }

  if (tabTask) tabTask.addEventListener('click', () => switchView('tasks'));
  if (tabStage) tabStage.addEventListener('click', () => switchView('stages'));
  if (tabTimeline) {
    tabTimeline.addEventListener('click', () => {
      applyFilter('all');
      if (timelineTitle) timelineTitle.textContent = 'All Cultivation Tips';
      switchView('timeline');
    });
  }

  // 3. Task Rows (Photo 1 -> Photo 2 Transition)
  container.querySelectorAll('.plantix-task-item').forEach(item => {
    item.addEventListener('click', () => {
      const taskId = item.getAttribute('data-task-id');
      const taskName = item.querySelector('.task-name')?.textContent?.trim() || 'Cultivation Tips';
      if (timelineTitle) timelineTitle.textContent = taskName;
      
      applyFilter(taskId);
      switchView('timeline');
      scrollToTips();
    });
  });

  // 4. Stage Rows (By Stage -> Timeline Transition)
  container.querySelectorAll('.plantix-stage-item').forEach(item => {
    item.addEventListener('click', () => {
      const stageId = item.getAttribute('data-stage-id');
      const stageName = item.querySelector('.task-name')?.textContent?.trim() || 'Cultivation Stage';
      if (timelineTitle) timelineTitle.textContent = stageName;

      applyFilterByStage(stageId);
      switchView('timeline');
      scrollToTips();
    });
  });

  // 5. Back Button in Timeline View
  if (btnBackToTasks) {
    btnBackToTasks.addEventListener('click', () => {
      switchView(lastActiveView || 'tasks');
      scrollToTips();
    });
  }

  // 6. Timeline Card Filtering Logic
  function applyFilter(filterKey) {
    filterPills.forEach(pill => {
      pill.classList.toggle('active', pill.getAttribute('data-filter') === filterKey);
    });

    visualCards.forEach(card => {
      const cardTask = card.getAttribute('data-task');
      const visible = (filterKey === 'all' || cardTask === filterKey);
      card.style.display = visible ? '' : 'none';
    });

    updateGroupBlockVisibility();
  }

  function applyFilterByStage(stageKey) {
    filterPills.forEach(pill => pill.classList.remove('active'));

    visualCards.forEach(card => {
      const cardStage = card.getAttribute('data-stage');
      const visible = (cardStage === stageKey);
      card.style.display = visible ? '' : 'none';
    });

    updateGroupBlockVisibility();
  }

  function updateGroupBlockVisibility() {
    groupBlocks.forEach(group => {
      const visibleCardsInGroup = group.querySelectorAll('.plantix-visual-card:not([style*="display: none"])');
      group.style.display = (visibleCardsInGroup.length > 0) ? '' : 'none';
    });
  }

  filterPills.forEach(pill => {
    pill.addEventListener('click', () => {
      const filterKey = pill.getAttribute('data-filter');
      const filterText = pill.textContent.trim();
      if (timelineTitle) {
        timelineTitle.textContent = filterKey === 'all' ? 'All Cultivation Tips' : filterText;
      }
      applyFilter(filterKey);
    });
  });

  // 7. "Read More" Modal Details Injection & Display
  function openCardModal(cardEl) {
    const jsonScript = cardEl.querySelector('.card-detail-json');
    if (!jsonScript) return;

    let data;
    try {
      data = JSON.parse(jsonScript.textContent);
    } catch (e) {
      console.error('Failed to parse card data:', e);
      return;
    }

    if (modalImg) modalImg.src = data.image || '';
    if (modalBadge) modalBadge.textContent = data.tag || 'Tip';
    if (modalHeading) modalHeading.textContent = data.title || '';
    if (modalSummary) modalSummary.textContent = data.summary || '';

    // Why Matters Box
    if (modalWhyBox && modalWhyText) {
      if (data.why) {
        modalWhyText.textContent = data.why;
        modalWhyBox.style.display = '';
      } else {
        modalWhyBox.style.display = 'none';
      }
    }

    // Materials List
    if (modalMaterialsList) {
      modalMaterialsList.innerHTML = '';
      if (Array.isArray(data.materials) && data.materials.length) {
        data.materials.forEach(mat => {
          const li = document.createElement('li');
          li.textContent = mat;
          modalMaterialsList.appendChild(li);
        });
        modalMaterialsList.parentElement.style.display = '';
      } else {
        modalMaterialsList.parentElement.style.display = 'none';
      }
    }

    // Steps List
    if (modalStepsList) {
      modalStepsList.innerHTML = '';
      if (Array.isArray(data.steps) && data.steps.length) {
        data.steps.forEach(step => {
          const li = document.createElement('li');
          li.textContent = step;
          modalStepsList.appendChild(li);
        });
        modalStepsList.parentElement.style.display = '';
      } else {
        modalStepsList.parentElement.style.display = 'none';
      }
    }

    // Pro-Tip Box
    if (modalProTipBox && modalProTipText) {
      if (data.pro_tip) {
        modalProTipText.textContent = data.pro_tip;
        modalProTipBox.style.display = '';
      } else {
        modalProTipBox.style.display = 'none';
      }
    }

    // Tool Shortcut Button
    if (modalToolBtn && modalToolName) {
      if (data.tool_url) {
        modalToolBtn.href = data.tool_url;
        modalToolName.textContent = data.tool_name || 'Open Tool';
        modalToolBtn.style.display = '';
      } else {
        modalToolBtn.style.display = 'none';
      }
    }

    // Show Modal
    if (modalBackdrop) {
      modalBackdrop.hidden = false;
      document.body.style.overflow = 'hidden';
    }
  }

  function closeModal() {
    if (modalBackdrop) {
      modalBackdrop.hidden = true;
      document.body.style.overflow = '';
    }
  }

  // Open modal on "Read more" click
  container.addEventListener('click', (e) => {
    const readMoreBtn = e.target.closest('.plantix-read-more-link');
    if (readMoreBtn) {
      e.preventDefault();
      const card = readMoreBtn.closest('.plantix-visual-card');
      if (card) openCardModal(card);
    }
  });

  if (modalCloseBtn) modalCloseBtn.addEventListener('click', closeModal);
  if (modalBackdrop) {
    modalBackdrop.addEventListener('click', (e) => {
      if (e.target === modalBackdrop) closeModal();
    });
  }

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && modalBackdrop && !modalBackdrop.hidden) {
      closeModal();
    }
  });

})();
