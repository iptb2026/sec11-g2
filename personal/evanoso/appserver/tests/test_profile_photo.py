import base64
from io import BytesIO
from PIL import Image
from test_bembank import BankingTests


class ProfilePhotoTests(BankingTests):
    def test_photo_upload_persistence_isolation_and_removal(self):
        output = BytesIO()
        Image.new('RGB', (400, 300), 'blue').save(output, format='PNG')
        payload = {'image': 'data:image/png;base64,' + base64.b64encode(output.getvalue()).decode()}
        self.assertEqual(self.client.put('/auth/profile-photo', json=payload).status_code, 401)
        response = self.client.put('/auth/profile-photo', headers=self.alice, json=payload)
        self.assertEqual(response.status_code, 200, response.text)
        saved = response.json()['profile_photo']
        with Image.open(BytesIO(base64.b64decode(saved.split(',')[1]))) as image:
            self.assertEqual(image.size, (256, 256))
            self.assertEqual(image.format, 'JPEG')
        self.assertEqual(self.client.get('/auth/profile-photo', headers=self.login('alice')).json()['profile_photo'], saved)
        self.assertIsNone(self.client.get('/auth/profile-photo', headers=self.bob).json()['profile_photo'])
        self.assertEqual(self.client.put('/auth/profile-photo', headers=self.alice, json={'image': 'data:image/jpeg;base64,bm90LWFuLWltYWdl'}).status_code, 400)
        self.assertEqual(self.client.put('/auth/profile-photo', headers=self.alice, json={'image': 'x' * 400001}).status_code, 422)
        self.assertEqual(self.client.get('/auth/profile-photo', headers=self.alice).json()['profile_photo'], saved)
        self.assertEqual(self.client.delete('/auth/profile-photo', headers=self.alice).status_code, 204)
        self.assertIsNone(self.client.get('/auth/profile-photo', headers=self.alice).json()['profile_photo'])
