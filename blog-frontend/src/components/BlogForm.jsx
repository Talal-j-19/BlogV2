import { useState } from "react";
import {
  Box,
  Button,
  FormControl,
  FormLabel,
  Input,
  VStack,
  HStack,
  Switch,
  useColorModeValue,
  Card,
  CardBody,
  Heading,
} from "@chakra-ui/react";

const BlogForm = ({ onSubmit, isGenerating }) => {
  const [formData, setFormData] = useState({
    topic: "",
    author: "Talal",
    generate_images: false,
    find_keywords: false,
  });

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value,
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(formData);
  };

  const cardBg = useColorModeValue("white", "gray.800");

  return (
    <Card bg={cardBg} boxShadow="lg" borderRadius="xl" overflow="hidden">
      <CardBody p={8}>
        <form onSubmit={handleSubmit}>
          <VStack spacing={6} align="stretch">
            <Heading size="lg" color="brand.700">
              Generate New Blog Post
            </Heading>
            
            <FormControl isRequired>
              <FormLabel>Blog Topic</FormLabel>
              <Input
                name="topic"
                value={formData.topic}
                onChange={handleChange}
                placeholder="Enter your blog topic..."
                size="lg"
                bg="white"
              />
            </FormControl>

            <FormControl>
              <FormLabel>Author Name</FormLabel>
              <Input
                name="author"
                value={formData.author}
                onChange={handleChange}
                placeholder="Author name"
                size="md"
                bg="white"
              />
            </FormControl>

            <VStack align="stretch" spacing={4}>
              <HStack justify="space-between">
                <FormLabel mb={0}>Generate Images</FormLabel>
                <Switch
                  name="generate_images"
                  isChecked={formData.generate_images}
                  onChange={handleChange}
                  colorScheme="brand"
                />
              </HStack>

              <HStack justify="space-between">
                <FormLabel mb={0}>Find Low Competition Keywords</FormLabel>
                <Switch
                  name="find_keywords"
                  isChecked={formData.find_keywords}
                  onChange={handleChange}
                  colorScheme="brand"
                />
              </HStack>
            </VStack>

            <Button
              type="submit"
              colorScheme="brand"
              size="lg"
              width="full"
              isLoading={isGenerating}
              loadingText="Generating..."
              _hover={{ transform: "translateY(-2px)", boxShadow: "lg" }}
              transition="all 0.2s"
            >
              Generate Blog Post
            </Button>
          </VStack>
        </form>
      </CardBody>
    </Card>
  );
};

export default BlogForm;
