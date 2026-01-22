#!/bin/bash
if [ $# -eq 0 ]; then
  echo "Usage: $0 <worktree-name>"
  echo "Error: Worktree 이름을 명시해주세요."
  exit 1
fi

ARGUMENT=$1
WORKTREE_PATH="../worktree/$ARGUMENT"

# Create the worktree, and if successful, change directory
if git worktree add "$WORKTREE_PATH"; then
  echo "Worktree 생성 성공: $WORKTREE_PATH"
  cd "$WORKTREE_PATH" || exit 1
  echo "- 디렉토리 변경 완료 : $(pwd)"
  claude
else
  echo "Worktree 생성 실패"
  exit 1
fi
