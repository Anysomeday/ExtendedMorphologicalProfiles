import numpy as np
from skimage.morphology import reconstruction
from skimage.morphology import erosion
from skimage.morphology import disk
from skimage import util
from skimage import io


class ExtendedMorphologicalProfiles:

    def build_emp(self, base_image, se_size=4, se_size_increment=2, num_openings_closings=4):
        self.base_image = base_image
        base_image_rows, base_image_columns, base_image_channels = self.base_image.shape
        se_size = se_size
        se_size_increment = se_size_increment
        num_openings_closings = num_openings_closings
        self.morphological_profile_size = (num_openings_closings * 2) + 1
        self.emp_size = self.morphological_profile_size * base_image_channels
        self.emp = np.zeros(
            shape=(base_image_rows, base_image_columns, self.emp_size))

        cont = 0
        for i in range(base_image_channels):
            # build MPs
            mp_temp = self.build_morphological_profiles(
                base_image[:, :, i], se_size, se_size_increment, num_openings_closings)

            aux = self.morphological_profile_size * (i+1)

            # build the EMP
            cont_aux = 0
            for k in range(cont, aux):
                self.emp[:, :, k] = mp_temp[:, :, cont_aux]
                cont_aux += 1

            cont = self.morphological_profile_size * (i+1)

        return self.emp

    def build_morphological_profiles(self, image, se_size=4, se_size_increment=2, num_openings_closings=4):
        x, y = image.shape

        cbr = np.zeros(shape=(x, y, num_openings_closings))
        obr = np.zeros(shape=(x, y, num_openings_closings))

        it = 0
        tam = se_size
        while it < num_openings_closings:
            se = disk(tam)
            temp = self.closing_by_reconstruction(image, se)
            cbr[:, :, it] = temp[:, :]
            temp = self.opening_by_reconstruction(image, se)
            obr[:, :, it] = temp[:, :]
            tam += se_size_increment
            it += 1

        mp = np.zeros(shape=(x, y, (num_openings_closings*2)+1))
        cont = num_openings_closings - 1
        for i in range(num_openings_closings):
            mp[:, :, i] = cbr[:, :, cont]
            cont = cont - 1

        mp[:, :, num_openings_closings] = image[:, :]

        cont = 0
        for i in range(num_openings_closings+1, num_openings_closings*2+1):
            mp[:, :, i] = obr[:, :, cont]
            cont += 1

        return mp

    def opening_by_reconstruction(self, image, se):
        eroded = erosion(image, se)
        reconstructed = reconstruction(eroded, image)
        return reconstructed

    def closing_by_reconstruction(self, image, se):
        obr = self.opening_by_reconstruction(image, se)

        obr_inverted = util.invert(obr)
        obr_inverted_eroded = erosion(obr_inverted, se)
        obr_inverted_eroded_rec = reconstruction(
            obr_inverted_eroded, obr_inverted)
        obr_inverted_eroded_rec_inverted = util.invert(obr_inverted_eroded_rec)
        return obr_inverted_eroded_rec_inverted

    def get_emp(self):
        return self.emp

    def get_base_image(self):
        return self.base_image

    def get_emp_size(self):
        return self.emp_size

    def get_morphological_profile_size(self):
        return self.morphological_profile_size

    def get_number_of_base_images(self):
        base_image_rows, base_image_columns, base_image_channels = self.base_image.shape
        return base_image_channels
