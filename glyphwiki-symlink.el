(defun dump-symlink ()
  (interactive)
  (cd "~/Resources/GlyphWiki/dump/work")
  (with-temp-buffer
    (insert-file-contents "~/Resources/GlyphWiki/dump/dump_newest_only.txt")
    (goto-char (point-min))
    (while (re-search-forward "^ \\(u[0-9a-f][-0-9a-z]+\\) .+| 99:0:0:0:0:200:200:\\(u[0-9a-f][-0-9a-z]+\\)$" nil t)
      (let ((link (match-string 1))
            (target (match-string 2)))
        (call-process "mv" nil nil nil (concat link ".svg") (concat link ".svg.bak"))
        (call-process "ln" nil nil nil "-s" (concat target ".svg") (concat link ".svg"))))) )

(princ "Now cleaning up symbolic links...\n")
(dump-symlink)
