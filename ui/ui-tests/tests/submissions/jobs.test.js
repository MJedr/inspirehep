const { routes } = require('../../utils/constants');
const { login, logout } = require('../../utils/user');
const { takeScreenShotForDesktop } = require('../../utils/screenshot');
const { createPollyInstance } = require('../../utils/polly');

describe('Jobs Submission', () => {
  beforeAll(async () => {
    await login();
  });

  it('matches screenshot for author submission form', async () => {
    const polly = await createPollyInstance('JobSubmission');

    await page.goto(routes.private.jobSubmission, {
      waitUntil: 'networkidle0',
    });

    const image = await takeScreenShotForDesktop(page);
    expect(image).toMatchImageSnapshot();

    await polly.stop();
  });

  afterAll(async () => {
    await logout();
  });
});
