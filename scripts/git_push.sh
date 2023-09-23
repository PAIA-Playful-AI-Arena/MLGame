git checkout master
latest_tag=$(git describe --tags $(git rev-list --tags --max-count=1))

git push github master develop $latest_tag
git push gitlab --all
git push gitlab --tags
git push paia --all
git push paia --tags
git checkout develop