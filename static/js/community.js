/**
 * Krishi Mitra - Farmer Community Frontend Engine
 * Real-time voting, live replies with author notification, workable share modal,
 * workable live translation, exact published timestamp, and admin deletion links.
 */

// CSRF Helper
function getCsrfToken() {
  const input = document.querySelector('input[name="csrfmiddlewaretoken"]');
  if (input && input.value) return input.value;
  const match = document.cookie.match(/csrftoken=([^;]+)/);
  if (match) return decodeURIComponent(match[1]);
  return '';
}

// Global active share data
let currentShareData = {
  title: '',
  url: ''
};

// ─── 1. GLOBAL POST VOTING (LIKE / DISLIKE) ───
window.votePost = async function(postId, action, btnEl) {
  if (!postId || !action) return;

  const card = document.getElementById(`post-${postId}`) || (btnEl ? btnEl.closest('.community-card') : null);
  const likeBtn = card ? card.querySelector('.btn-like') : null;
  const dislikeBtn = card ? card.querySelector('.btn-dislike') : null;
  const likeCountEl = document.getElementById(`likeCount-${postId}`);
  const dislikeCountEl = document.getElementById(`dislikeCount-${postId}`);

  if (btnEl) {
    btnEl.style.transform = 'scale(0.92)';
    setTimeout(() => { btnEl.style.transform = ''; }, 150);
  }

  try {
    const formData = new FormData();
    formData.append('csrfmiddlewaretoken', getCsrfToken());
    formData.append('action', action);

    const res = await fetch(`/community/post/${postId}/vote/`, {
      method: 'POST',
      headers: {
        'X-CSRFToken': getCsrfToken(),
        'X-Requested-With': 'XMLHttpRequest'
      },
      body: formData
    });

    if (!res.ok) throw new Error('Vote request failed');
    const data = await res.json();

    if (data.success) {
      if (likeCountEl) likeCountEl.textContent = data.likes;
      if (dislikeCountEl) dislikeCountEl.textContent = data.dislikes;

      if (likeBtn) likeBtn.classList.toggle('is-active', data.current_vote === 'like');
      if (dislikeBtn) dislikeBtn.classList.toggle('is-active', data.current_vote === 'dislike');
    }
  } catch (err) {
    console.error('Error voting on post:', err);
  }
};

// ─── 2. ANSWER / REPLY VOTING ───
window.voteAnswer = async function(answerId, btnEl) {
  if (!answerId) return;

  if (btnEl) {
    btnEl.style.transform = 'scale(0.92)';
    setTimeout(() => { btnEl.style.transform = ''; }, 150);
  }

  try {
    const formData = new FormData();
    formData.append('csrfmiddlewaretoken', getCsrfToken());
    formData.append('action', 'like');

    const res = await fetch(`/community/answer/${answerId}/vote/`, {
      method: 'POST',
      headers: {
        'X-CSRFToken': getCsrfToken(),
        'X-Requested-With': 'XMLHttpRequest'
      },
      body: formData
    });

    if (!res.ok) throw new Error('Answer vote failed');
    const data = await res.json();

    if (data.success) {
      const countEl = document.getElementById(`ansLikeCount-${answerId}`);
      if (countEl) countEl.textContent = data.likes;
      if (btnEl) btnEl.classList.toggle('is-active', data.current_vote === 'like');
    }
  } catch (err) {
    console.error('Error voting on answer:', err);
  }
};

// ─── 3. TOGGLE ANSWERS DRAWER ───
window.toggleAnswers = function(postId, focusInput = false) {
  const drawer = document.getElementById(`answersDrawer-${postId}`);
  const card = document.getElementById(`post-${postId}`);
  if (!drawer) return;

  const isOpen = drawer.classList.contains('is-open');
  if (isOpen && !focusInput) {
    drawer.classList.remove('is-open');
    if (card) {
      const toggleChevron = card.querySelector('.toggle-chevron');
      if (toggleChevron) toggleChevron.style.transform = '';
    }
  } else {
    drawer.classList.add('is-open');
    if (card) {
      const toggleChevron = card.querySelector('.toggle-chevron');
      if (toggleChevron) toggleChevron.style.transform = 'rotate(180deg)';
    }
    if (focusInput) {
      const input = document.getElementById(`replyInput-${postId}`);
      if (input) {
        setTimeout(() => input.focus(), 150);
      }
    }
  }
};

// ─── 4. SUBMIT INLINE ANSWER (NOTIFIES POST AUTHOR DIRECTLY) ───
window.submitAnswer = async function(event, postId) {
  event.preventDefault();
  const input = document.getElementById(`replyInput-${postId}`);
  const btn = document.getElementById(`replyBtn-${postId}`);
  const list = document.getElementById(`answersList-${postId}`);
  const countEl = document.getElementById(`answersCount-${postId}`);
  const countHeaderEl = document.getElementById(`answersCountHeader-${postId}`);
  const emptyEl = document.getElementById(`emptyAnswers-${postId}`);

  if (!input || !input.value.trim()) return;

  const originalContent = input.value.trim();
  const originalBtnHtml = btn ? btn.innerHTML : '';
  if (btn) {
    btn.disabled = true;
    btn.innerHTML = `<span class="spinner-border spinner-border-sm me-1" role="status"></span> Posting...`;
  }

  try {
    const formData = new FormData();
    formData.append('content', originalContent);

    const res = await fetch(`/community/post/${postId}/answer/`, {
      method: 'POST',
      headers: {
        'X-CSRFToken': getCsrfToken(),
        'X-Requested-With': 'XMLHttpRequest'
      },
      body: formData
    });

    if (!res.ok) throw new Error('Failed to post answer');
    const data = await res.json();

    if (data.success && data.answer) {
      if (emptyEl) emptyEl.remove();

      const newAnswerHtml = `
        <div class="community-answer-item is-new-answer" id="answer-${data.answer.id}" style="animation: fadeInScale 0.25s ease;">
          <div class="answer-header">
            <div class="answer-author-wrap">
              <span class="answer-avatar">${data.answer.author_name.charAt(0).toUpperCase()}</span>
              <div>
                <strong class="answer-author-name">${data.answer.author_name}</strong>
                <span class="answer-role-badge">${data.answer.author_role}</span>
              </div>
            </div>
            <span class="answer-time" title="Just now">
              <i class="bi bi-clock me-1"></i>${data.answer.exact_time || 'Just now'}
            </span>
          </div>
          <div class="answer-content">
            <p>${data.answer.content}</p>
          </div>
          <div class="answer-footer-row">
            <button type="button" class="btn-answer-like" onclick="voteAnswer(${data.answer.id}, this)" title="Mark solution as helpful">
              <i class="bi bi-hand-thumbs-up me-1"></i>
              <span class="ans-like-count" id="ansLikeCount-${data.answer.id}">0</span>
            </button>
          </div>
        </div>
      `;

      if (list) list.insertAdjacentHTML('beforeend', newAnswerHtml);
      if (countEl) countEl.textContent = data.answers_count;
      if (countHeaderEl) countHeaderEl.textContent = data.answers_count;

      input.value = '';
      if (typeof window.showKrishiToast === 'function') {
        window.showKrishiToast('Your answer was posted! The author has been sent a direct notification.', true);
      }
    }
  } catch (err) {
    console.error('Answer submission error:', err);
    alert('Could not submit answer. Please try again.');
  } finally {
    if (btn) {
      btn.disabled = false;
      btn.innerHTML = originalBtnHtml;
    }
  }
};

// ─── 5. WORKABLE SHARE MODAL & CHANNELS ───
window.openShareModal = function(postId, title, relativeOrFullUrl) {
  const fullUrl = (relativeOrFullUrl && relativeOrFullUrl.startsWith('http'))
    ? relativeOrFullUrl
    : (window.location.origin + (relativeOrFullUrl || `/community/post/${postId}/`));
  currentShareData.title = title || 'Krishi Mitra Agricultural Community';
  currentShareData.url = fullUrl;

  // Update modal elements
  const inputEl = document.getElementById('shareLinkInput');
  if (inputEl) inputEl.value = fullUrl;

  const copyBtnText = document.getElementById('copyBtnText');
  if (copyBtnText) copyBtnText.textContent = 'Copy';

  const shareText = `Agricultural Question on Krishi Mitra: "${currentShareData.title}"\nCheck out the solutions here: ${fullUrl}`;
  const encodedText = encodeURIComponent(shareText);
  const encodedUrl = encodeURIComponent(fullUrl);

  const waBtn = document.getElementById('shareWhatsAppBtn');
  if (waBtn) waBtn.href = `https://api.whatsapp.com/send?text=${encodedText}`;

  const tgBtn = document.getElementById('shareTelegramBtn');
  if (tgBtn) tgBtn.href = `https://t.me/share/url?url=${encodedUrl}&text=${encodeURIComponent(currentShareData.title)}`;

  const twBtn = document.getElementById('shareTwitterBtn');
  if (twBtn) twBtn.href = `https://twitter.com/intent/tweet?text=${encodeURIComponent(currentShareData.title)}&url=${encodedUrl}`;

  // Open modal via Bootstrap or fallback
  const modalEl = document.getElementById('communityShareModal');
  if (modalEl) {
    if (window.bootstrap && window.bootstrap.Modal) {
      const modal = window.bootstrap.Modal.getOrCreateInstance(modalEl);
      modal.show();
    } else {
      modalEl.classList.add('show');
      modalEl.style.display = 'block';
      let backdrop = document.getElementById('modalBackdropFallback');
      if (!backdrop) {
        backdrop = document.createElement('div');
        backdrop.id = 'modalBackdropFallback';
        backdrop.className = 'modal-backdrop fade show';
        document.body.appendChild(backdrop);
      }
    }
  } else if (navigator.share) {
    // If modal not available, use native share directly
    navigator.share({ title: currentShareData.title, text: shareText, url: fullUrl }).catch(() => {});
  }
};

window.copyShareLink = function() {
  const inputEl = document.getElementById('shareLinkInput');
  const copyBtnText = document.getElementById('copyBtnText');
  if (!inputEl) return;

  inputEl.select();
  navigator.clipboard.writeText(inputEl.value).then(() => {
    if (copyBtnText) copyBtnText.textContent = 'Copied!';
    if (typeof window.showKrishiToast === 'function') {
      window.showKrishiToast('Link copied to clipboard!', true);
    }
    setTimeout(() => {
      if (copyBtnText) copyBtnText.textContent = 'Copy';
    }, 2000);
  }).catch(() => {
    document.execCommand('copy');
    if (copyBtnText) copyBtnText.textContent = 'Copied!';
  });
};

window.triggerNativeShare = function() {
  if (navigator.share) {
    navigator.share({
      title: currentShareData.title,
      text: `Agricultural Question on Krishi Mitra: "${currentShareData.title}"`,
      url: currentShareData.url
    }).catch(() => {});
  } else {
    window.copyShareLink();
  }
};

// ─── 6. WORKABLE TRANSLATE FEATURE ───
window.toggleTranslation = async function(btn, postId) {
  const card = document.getElementById(`post-${postId}`) || btn.closest('.community-card');
  if (!card) return;

  const titleEl = document.getElementById(`postTitle-${postId}`);
  const descEl = document.getElementById(`postDesc-${postId}`);
  const labelEl = btn.querySelector('.translate-label') || btn.querySelector('span');

  const isTranslated = btn.getAttribute('data-translated') === 'true';

  if (isTranslated) {
    // Revert to original text
    const originalTitle = btn.getAttribute('data-orig-title');
    const originalDesc = btn.getAttribute('data-orig-desc');

    if (titleEl && originalTitle) {
      const a = titleEl.querySelector('a');
      if (a) a.textContent = originalTitle;
      else titleEl.textContent = originalTitle;
    }
    if (descEl && originalDesc) {
      const p = descEl.querySelector('.post-text-body') || descEl.querySelector('p');
      if (p) p.textContent = originalDesc;
    }

    btn.setAttribute('data-translated', 'false');
    btn.classList.remove('is-active');
    if (labelEl) labelEl.textContent = 'Translate';

    if (typeof window.showKrishiToast === 'function') {
      window.showKrishiToast('Showing original text');
    }
  } else {
    // Perform translation
    const originalBtnHtml = btn.innerHTML;
    if (labelEl) labelEl.textContent = 'Translating…';
    btn.disabled = true;

    try {
      const res = await fetch(`/community/post/${postId}/translate/?lang=hi`, {
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
      });
      if (!res.ok) throw new Error('Translation failed');
      const data = await res.json();

      if (data.success) {
        // Save original text
        btn.setAttribute('data-orig-title', data.original_title);
        btn.setAttribute('data-orig-desc', data.original_desc);
        btn.setAttribute('data-translated', 'true');

        // Apply translated title
        if (titleEl && data.title) {
          const a = titleEl.querySelector('a');
          if (a) a.textContent = data.title;
          else titleEl.textContent = data.title;
        }

        // Apply translated description
        if (descEl && data.description) {
          const p = descEl.querySelector('.post-text-body') || descEl.querySelector('p');
          if (p) p.textContent = data.description;
        }

        btn.classList.add('is-active');
        if (labelEl) labelEl.textContent = `Translated (${data.target_lang}) · Original`;

        if (typeof window.showKrishiToast === 'function') {
          window.showKrishiToast(`Translated to ${data.target_lang}`, true);
        }
      }
    } catch (err) {
      console.error('Translation error:', err);
      if (typeof window.showKrishiToast === 'function') {
        window.showKrishiToast('Translation service unavailable. Please try again.', false);
      }
    } finally {
      btn.disabled = false;
      if (!btn.getAttribute('data-translated') || btn.getAttribute('data-translated') === 'false') {
        btn.innerHTML = originalBtnHtml;
      }
    }
  }
};

// ─── 7. USER NOTIFICATIONS MODAL & REPLIES ───
window.openNotificationsModal = function() {
  const modalEl = document.getElementById('communityNotifModal');
  if (modalEl) {
    if (window.bootstrap && window.bootstrap.Modal) {
      const modal = window.bootstrap.Modal.getOrCreateInstance(modalEl);
      modal.show();
    } else {
      modalEl.classList.add('show');
      modalEl.style.display = 'block';
      let backdrop = document.getElementById('modalBackdropFallback');
      if (!backdrop) {
        backdrop = document.createElement('div');
        backdrop.id = 'modalBackdropFallback';
        backdrop.className = 'modal-backdrop fade show';
        document.body.appendChild(backdrop);
      }
    }
  }
  window.fetchNotificationsList();
};
window.toggleNotificationsModal = window.openNotificationsModal;

window.fetchNotificationsList = async function() {
  try {
    const res = await fetch('/community/api/notifications/', {
      headers: { 'X-Requested-With': 'XMLHttpRequest' }
    });
    if (!res.ok) return;
    const data = await res.json();
    if (!data.success) return;

    const badge = document.getElementById('notifBadge');
    if (badge) {
      badge.textContent = data.unread_count;
      badge.classList.toggle('d-none', data.unread_count <= 0);
    }

    const listEl = document.getElementById('notificationItemsList');
    if (listEl && data.notifications && data.notifications.length > 0) {
      listEl.innerHTML = data.notifications.map(n => `
        <a href="/community/post/${n.post_id}/" class="notif-item-card ${n.is_read ? '' : 'is-unread'}" onclick="dismissNotifModal()">
          <div class="notif-avatar">
            <span>${(n.actor_name || 'U').charAt(0).toUpperCase()}</span>
          </div>
          <div class="notif-content">
            <strong class="notif-title">${n.title}</strong>
            <p class="notif-message">${n.message}</p>
            <div class="notif-meta">
              <span class="notif-actor">${n.actor_name} (${n.actor_role})</span>
              <span class="notif-time">${n.created_at}</span>
            </div>
          </div>
        </a>
      `).join('');
    }
  } catch (e) {
    console.debug('Notification fetch error:', e);
  }
};

window.dismissNotifModal = function() {
  const modalEl = document.getElementById('communityNotifModal');
  if (modalEl) {
    if (window.bootstrap && window.bootstrap.Modal) {
      const modal = window.bootstrap.Modal.getInstance(modalEl);
      if (modal) modal.hide();
    }
    modalEl.classList.remove('show');
    modalEl.style.display = 'none';
  }
  const backdrop = document.getElementById('modalBackdropFallback');
  if (backdrop) backdrop.remove();
  document.body.classList.remove('modal-open');
};

window.markAllNotificationsRead = async function() {
  try {
    const formData = new FormData();
    formData.append('csrfmiddlewaretoken', getCsrfToken());

    const res = await fetch('/community/api/notifications/read/', {
      method: 'POST',
      headers: {
        'X-CSRFToken': getCsrfToken(),
        'X-Requested-With': 'XMLHttpRequest'
      },
      body: formData
    });

    if (res.ok) {
      const badge = document.getElementById('notifBadge');
      if (badge) {
        badge.textContent = '0';
        badge.classList.add('d-none');
      }

      document.querySelectorAll('.notif-item-card.is-unread').forEach(el => {
        el.classList.remove('is-unread');
      });

      const statusText = document.getElementById('notifStatusText');
      if (statusText) statusText.textContent = 'All notifications marked as read';

      if (typeof window.showKrishiToast === 'function') {
        window.showKrishiToast('All notifications marked as read', true);
      }
    }
  } catch (err) {
    console.error('Error marking notifications read:', err);
  }
};

// Global click handler to dismiss modals cleanly
document.addEventListener('click', function(e) {
  const closeBtn = e.target.closest('[data-bs-dismiss="modal"]');
  if (closeBtn) {
    const modal = closeBtn.closest('.modal');
    if (modal) {
      if (window.bootstrap && window.bootstrap.Modal) {
        const inst = window.bootstrap.Modal.getInstance(modal);
        if (inst) inst.hide();
      }
      modal.classList.remove('show');
      modal.style.display = 'none';
      const backdrop = document.getElementById('modalBackdropFallback');
      if (backdrop) backdrop.remove();
      document.body.classList.remove('modal-open');
    }
  }
});

// ─── 8. ASK COMMUNITY: IMAGE PREVIEW & REMOVAL ───
window.handleImageSelection = function(event) {
  const file = event.target.files[0];
  if (!file) return;

  const reader = new FileReader();
  reader.onload = function(e) {
    const previewWrap = document.getElementById('askImagePreviewWrap');
    const previewImg = document.getElementById('askImagePreview');
    if (previewWrap && previewImg) {
      previewImg.src = e.target.result;
      previewWrap.classList.remove('d-none');
    }
  };
  reader.readAsDataURL(file);
};

window.removeImagePreview = function() {
  const input = document.getElementById('askImageInput');
  const previewWrap = document.getElementById('askImagePreviewWrap');
  const previewImg = document.getElementById('askImagePreview');
  if (input) input.value = '';
  if (previewImg) previewImg.src = '';
  if (previewWrap) previewWrap.classList.add('d-none');
};

// ─── 9. ASK COMMUNITY: CROP PICKER ───
window.toggleCropPicker = function() {
  const sheet = document.getElementById('cropsPickerSheet');
  if (sheet) sheet.classList.toggle('d-none');
};

window.selectCrop = function(cropName, cropIcon) {
  const hiddenInput = document.getElementById('selectedCropInput');
  const displaySpan = document.getElementById('selectedCropDisplay');
  const sheet = document.getElementById('cropsPickerSheet');
  const pickerBtn = document.getElementById('openCropPickerBtn');

  if (hiddenInput) hiddenInput.value = cropName;
  if (displaySpan) displaySpan.innerHTML = `<span class="me-1">${cropIcon}</span> ${cropName}`;
  if (pickerBtn) pickerBtn.classList.add('has-selection');
  if (sheet) sheet.classList.add('d-none');
};

// ─── 10. LIVE CHARACTER COUNTERS ───
window.updateCharCount = function(textarea, counterId, maxLen) {
  const counterEl = document.getElementById(counterId);
  if (!counterEl) return;
  const currentLen = textarea.value.length;
  counterEl.textContent = `${currentLen} / ${maxLen} Characters`;
  if (currentLen >= maxLen) counterEl.classList.add('text-danger');
  else counterEl.classList.remove('text-danger');
};
