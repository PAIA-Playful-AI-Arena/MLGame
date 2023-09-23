git checkout master
latest_tag=$(git describe --tags $(git rev-list --tags --max-count=1))

git push github master develop $latest_tag
git push gitlab master develop $latest_tag
git push paia master develop $latest_tag
